// ESLint flat config — extends Next.js core-web-vitals and TypeScript rules.
import { FlatCompat } from "@eslint/eslintrc";

const compat = new FlatCompat({
  baseDirectory: import.meta.dirname,
});

const eslintConfig = [
  ...compat.extends("next/core-web-vitals", "next/typescript"),
  {
    ignores: [
      "node_modules/**",
      ".next/**",
      ".next-build/**",
      "out/**",
      "design-guidance/**",
      ".seed-cache/**",
      "next-env.d.ts",
    ],
  },
];

export default eslintConfig;
