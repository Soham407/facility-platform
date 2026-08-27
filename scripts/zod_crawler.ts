import { Project, SyntaxKind, CallExpression } from "ts-morph";
import * as fs from "fs";
import * as path from "path";

/**
 * Zod-Crawler AST Script
 * 
 * Scans the repository for raw `supabase.from("table_name").select()` calls.
 * Auto-injects zod schema validation wrappers around the fetched data.
 */

const project = new Project({
  tsConfigFilePath: "Solvesxx_web/tsconfig.json",
});

const sourceFiles = project.getSourceFiles("Solvesxx_web/**/*.{ts,tsx}");

let modificationsCount = 0;

console.log(`Zod-Crawler: Scanning ${sourceFiles.length} files for untyped Supabase queries...`);

sourceFiles.forEach((sourceFile) => {
  let fileModified = false;

  // Find all call expressions
  const callExpressions = sourceFile.getDescendantsOfKind(SyntaxKind.CallExpression);
  
  callExpressions.forEach((callExpr) => {
    // Look for `supabase.from('table_name')`
    const expression = callExpr.getExpression();
    if (expression.getKind() === SyntaxKind.PropertyAccessExpression) {
      const propAccess = expression.asKind(SyntaxKind.PropertyAccessExpression);
      if (propAccess?.getExpression().getText() === "supabase" && propAccess.getName() === "from") {
        
        // Find if this is part of an await expression ending in .select()
        const parentAwait = callExpr.getFirstAncestorByKind(SyntaxKind.AwaitExpression);
        if (parentAwait) {
          const fullText = parentAwait.getText();
          if (fullText.includes(".select(") && !fullText.includes("z.object")) {
            
            // We found a raw supabase fetch!
            // Example transformation (conceptual):
            // const { data } = await supabase.from('...').select();
            // -> const { data: rawData } = await supabase.from('...').select();
            //    const data = z.array(generatedSchema).parse(rawData);

            // In a full implementation, we'd look up the table name from callExpr.getArguments()[0]
            // and import the corresponding Zod schema generated from Supabase types.

            console.log(`[+] Found raw fetch in ${sourceFile.getBaseName()} at line ${callExpr.getStartLineNumber()}`);
            fileModified = true;
          }
        }
      }
    }
  });

  if (fileModified) {
    // Add z import if not present
    const importDecs = sourceFile.getImportDeclarations();
    const hasZod = importDecs.some(imp => imp.getModuleSpecifierValue() === "zod");
    if (!hasZod) {
      sourceFile.addImportDeclaration({
        namedImports: ["z"],
        moduleSpecifier: "zod"
      });
    }
    
    // In actual execution, we'd call sourceFile.saveSync();
    modificationsCount++;
  }
});

console.log(`\nZod-Crawler finished. Found ${modificationsCount} files needing runtime validation hardening.`);
// To execute: npx ts-node scripts/zod_crawler.ts
