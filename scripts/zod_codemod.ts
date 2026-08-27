import { Project, SyntaxKind, VariableDeclaration, CallExpression, AwaitExpression, VariableStatement } from "ts-morph";
import * as fs from "fs";
import * as path from "path";

// Helper to convert snake_case table name to camelCaseRowSchema
function getSchemaName(tableName: string) {
  const camelCase = tableName.replace(/_([a-z])/g, (g) => g[1].toUpperCase());
  return `${camelCase}RowSchema`;
}

async function runCodemod() {
  const project = new Project({
    tsConfigFilePath: "Solvesxx_web/tsconfig.json",
  });

  const sourceFiles = project.getSourceFiles("Solvesxx_web/**/*.{ts,tsx}");
  let filesModified = 0;

  console.log(`Scanning ${sourceFiles.length} files...`);

  sourceFiles.forEach((sourceFile) => {
    let fileModified = false;
    const schemasToImport = new Set<string>();
    let needsZod = false;

    // Find all variable declarations
    const variableDeclarations = sourceFile.getDescendantsOfKind(SyntaxKind.VariableDeclaration);

    // We only want to process each variable declaration once
    const processedDeclarations = new Set<VariableDeclaration>();

    variableDeclarations.forEach((varDecl) => {
      if (processedDeclarations.has(varDecl)) return;

      const initializer = varDecl.getInitializer();
      if (!initializer || initializer.getKind() !== SyntaxKind.AwaitExpression) return;

      const awaitExpr = initializer.asKind(SyntaxKind.AwaitExpression);
      if (!awaitExpr) return;

      const callExpr = awaitExpr.getExpression().asKind(SyntaxKind.CallExpression);
      if (!callExpr) return;

      const callText = callExpr.getText();
      if (!callText.includes("supabase.from") || !callText.includes(".select")) return;

      // Ensure we haven't already wrapped this
      if (callText.includes(".parse(")) return;

      // Extract table name from supabase.from("table_name")
      const supabaseFromCall = callExpr.getDescendantsOfKind(SyntaxKind.CallExpression).find(c => {
        const expr = c.getExpression();
        if (expr.getKind() === SyntaxKind.PropertyAccessExpression) {
          const propAccess = expr.asKind(SyntaxKind.PropertyAccessExpression);
          return propAccess?.getExpression().getText() === "supabase" && propAccess?.getName() === "from";
        }
        return false;
      });

      if (!supabaseFromCall) return;

      const args = supabaseFromCall.getArguments();
      if (args.length === 0) return;
      
      const tableNameArg = args[0];
      if (tableNameArg.getKind() !== SyntaxKind.StringLiteral) return;
      
      const tableName = tableNameArg.getText().replace(/['"]/g, "");
      const schemaName = getSchemaName(tableName);
      schemasToImport.add(schemaName);

      const isSingle = callText.includes(".single()") || callText.includes(".maybeSingle()");

      const nameNode = varDecl.getNameNode();
      if (nameNode.getKind() === SyntaxKind.ObjectBindingPattern) {
        const objectBinding = nameNode.asKind(SyntaxKind.ObjectBindingPattern);
        const elements = objectBinding?.getElements();
        
        const dataElement = elements?.find(e => e.getPropertyNameNode()?.getText() === "data" || (!e.getPropertyNameNode() && e.getNameNode().getText() === "data"));
        
        if (dataElement) {
          // Destructuring assignment like { data: myData, error }
          const targetName = dataElement.getNameNode().getText();
          const propertyName = dataElement.getPropertyNameNode()?.getText() || "data";
          
          const rawVarName = `raw${targetName.charAt(0).toUpperCase() + targetName.slice(1)}`;
          
          // Rename the destructured variable
          if (propertyName === "data") {
            dataElement.replaceWithText(`data: ${rawVarName}`);
          } else {
            // It was already like data: alias
            dataElement.replaceWithText(`${propertyName}: ${rawVarName}`);
          }

          const varStatement = varDecl.getFirstAncestorByKind(SyntaxKind.VariableStatement);
          if (varStatement) {
            const parent = varStatement.getParent();
            if (parent) {
              const statementIndex = varStatement.getChildIndex();
              const parseStatement = isSingle 
                ? `const ${targetName} = ${rawVarName} ? ${schemaName}.passthrough().parse(${rawVarName}) : null;`
                : `const ${targetName} = ${rawVarName} ? z.array(${schemaName}.passthrough()).parse(${rawVarName}) : [];`;
              
              varStatement.getParent()?.insertStatements(varStatement.getChildIndex() + 1, parseStatement);
              fileModified = true;
              needsZod = true;
            }
          }
        }
      } else if (nameNode.getKind() === SyntaxKind.Identifier) {
        // e.g. const response = await supabase...
        const targetName = nameNode.getText();
        const rawVarName = `raw${targetName.charAt(0).toUpperCase() + targetName.slice(1)}`;
        
        varDecl.getNameNode().replaceWithText(rawVarName);
        
        const varStatement = varDecl.getFirstAncestorByKind(SyntaxKind.VariableStatement);
        if (varStatement) {
          const parseStatement = isSingle 
                ? `const ${targetName} = { ...${rawVarName}, data: ${rawVarName}.data ? ${schemaName}.passthrough().parse(${rawVarName}.data) : null };`
                : `const ${targetName} = { ...${rawVarName}, data: ${rawVarName}.data ? z.array(${schemaName}.passthrough()).parse(${rawVarName}.data) : [] };`;
          
          varStatement.getParent()?.insertStatements(varStatement.getChildIndex() + 1, parseStatement);
          fileModified = true;
          needsZod = true;
        }
      }
      
      processedDeclarations.add(varDecl);
    });

    if (fileModified) {
      if (needsZod) {
        const hasZod = sourceFile.getImportDeclarations().some(imp => imp.getModuleSpecifierValue() === "zod");
        if (!hasZod) {
          sourceFile.insertImportDeclaration(0, {
            namedImports: ["z"],
            moduleSpecifier: "zod"
          });
        }
      }

      if (schemasToImport.size > 0) {
        sourceFile.insertImportDeclaration(1, {
          namedImports: Array.from(schemasToImport),
          moduleSpecifier: "@/src/types/schema"
        });
      }

      sourceFile.saveSync();
      filesModified++;
      console.log(`[+] Modified ${sourceFile.getBaseName()}`);
    }
  });

  console.log(`\\nCodemod finished. Updated ${filesModified} files.`);
}

runCodemod().catch(console.error);
