import type { Meta, StoryObj } from "@storybook/vue3-vite";

import ReadoutStationState from "@/components/ReadoutStationState.vue";

const meta = {
  title: "Components / Readout Station State",
  component: ReadoutStationState,
} satisfies Meta<typeof ReadoutStationState>;

type Story = StoryObj<typeof meta>;

export default meta;

export const NoReadoutStation = {} satisfies Story;

export const StationDisconnected = {
  args: { name: "COM1", state: "disconnected" },
} satisfies Story;

export const StationConnecting = {
  args: { name: "COM1", state: "connecting" },
} satisfies Story;

export const StationReady = {
  args: { name: "COM1", state: "ready" },
};

export const StationReading = {
  args: { name: "COM1", state: "reading" },
};
