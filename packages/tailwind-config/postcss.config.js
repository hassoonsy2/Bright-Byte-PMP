// Import the plugin so it resolves from THIS package's node_modules
// (@tailwindcss/postcss is a dependency of @bright-byte/tailwind-config).
// The string-key form ({ "@tailwindcss/postcss": {} }) makes PostCSS resolve the
// plugin from the consuming app's directory instead, which fails under pnpm's
// isolated linker because the apps don't declare @tailwindcss/postcss themselves.
import tailwindcss from "@tailwindcss/postcss";

export default {
  plugins: [
    // "tailwindcss/nesting"
    tailwindcss(),
  ],
};
