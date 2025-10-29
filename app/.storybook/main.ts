import { StorybookConfig } from "@storybook/vue3-vite";

export default {
  "framework": "@storybook/vue3-vite",
  "stories": [
    "../src/**/*.mdx",
    "../src/**/*.stories.@(js|jsx|ts|tsx)"
  ],

  "addons": ["@storybook/addon-links", "@storybook/addon-docs"],
} satisfies StorybookConfig;
