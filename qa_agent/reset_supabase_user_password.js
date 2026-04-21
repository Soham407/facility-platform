const { createClient } = require('../Solvesxx_mobile/node_modules/@supabase/supabase-js');

const supabaseUrl =
  process.env.SUPABASE_URL || 'https://wwhbdgwfodumognpkgrf.supabase.co';
const serviceRoleKey = process.env.SUPABASE_SERVICE_ROLE_KEY || 'PASTE_SERVICE_ROLE_KEY_HERE';
const targetEmail = process.env.TARGET_EMAIL || 'rohit@test.com';
const newPassword = process.env.NEW_PASSWORD || 'Test@1234';

if (!serviceRoleKey || serviceRoleKey === 'PASTE_SERVICE_ROLE_KEY_HERE') {
  console.error('Missing SUPABASE_SERVICE_ROLE_KEY. Set it in your shell before running.');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, serviceRoleKey, {
  auth: {
    autoRefreshToken: false,
    persistSession: false,
  },
});

async function main() {
  const { data: list, error: listError } = await supabase.auth.admin.listUsers();
  if (listError) {
    throw listError;
  }

  const user = list.users.find((entry) => (entry.email || '').toLowerCase() === targetEmail.toLowerCase());
  if (!user) {
    throw new Error(`User not found: ${targetEmail}`);
  }

  const { data, error } = await supabase.auth.admin.updateUserById(user.id, {
    password: newPassword,
    email_confirm: true,
  });

  if (error) {
    throw error;
  }

  console.log(`Password reset for ${data.user.email}`);
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
