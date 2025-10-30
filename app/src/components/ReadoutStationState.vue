<template>
  <div
    class="w-32 relative text-pale-dawn-superdark"
    :class="{ 'animate-pulse': state === 'connecting' }"
  >
    <svg preserveAspectRatio="xMidYMid meet" viewBox="0 0 50 142">
      <!-- Station body -->
      <path
        :class="{
          'fill-ash-light': state === undefined,
          'fill-pale-dawn-semidark': state === 'disconnected',
          'fill-dawn-semidark':
            state === 'connecting' || state === 'ready' || state === 'reading',
        }"
        d="m 17,0 c -1.148233,0 -2.527971,1.145683 -2.5,2.594834 -3.273212,1.108152 -6.183135,3.62096 -8.384911,6.223997 -2.053642,2.427907 -4.025628,7.060355 -4.125896,10.28445 l -1.989193,63.896714 c -0.115311,3.70775 1.519182,8.59963 4.01104,11.26804 2.785128,2.98247 6.97993,5.69587 10.98896,5.73196 h 20 c 3.039728,0.0274 8.291062,-2.45351 10.315457,-4.79874 2.437827,-2.82419 4.795598,-8.4172 4.684544,-12.20126 L 48.108676,19.103281 c -0.115772,-3.945175 -2.675678,-8.903888 -5.216736,-11.848822 -2.142439,-2.482959 -5.134268,-4.150248 -7.39194,-4.898992 0,-1.148713 -1.36869,-2.355467 -2.5,-2.355467 z m 8,10.499997 c 3.872291,1e-6 7.250057,3.245301 7.25,7.25 -5.6e-5,4.004615 -3.37779,7.249999 -7.25,7.25 -3.872212,1e-6 -7.249943,-3.245382 -7.25,-7.25 -5.7e-5,-4.004701 3.377707,-7.250001 7.25,-7.25 z"
      />
      <!-- Cable -->
      <path
        v-if="state"
        class="stroke-5"
        :class="
          state === 'disconnected' || state === 'connecting'
            ? 'stroke-ash-semidark'
            : 'stroke-black'
        "
        style="stroke-linecap: butt; fill: none"
        d="m 25,99.967126 c 0,6.017754 -1.022531,26.318054 0.114653,31.987934 2.243446,11.18559 17.47742,7.34517 19.717228,3.83429 2.613092,-4.096 2.388496,-9.26041 -0.272594,-13.06082 -1.542121,-2.20236 -5.351453,-5.40907 -12.350029,-3.7997 -6.768655,1.5565 -16.677956,3.66023 -32.09737263,3.66023"
      />
      <!-- Data -->
      <path
        v-if="state === 'reading'"
        class="stroke-gras-superlight stroke-2 data-flow"
        d="m 25.005732,99.967126 c 0,6.017754 -1.022531,26.318054 0.114653,31.987934 2.243446,11.18559 17.47742,7.34517 19.717228,3.83429 2.613092,-4.096 2.388496,-9.26041 -0.272594,-13.06082 -1.542121,-2.20236 -4.601981,-5.55839 -11.600557,-3.94902 -1.313406,0.30203 -3.910511,0.81548 -5.670565,1.16896 m -6.006686,1.15338 c -5.664128,0.88326 -12.3303867,1.48721 -21.1695941,1.48721"
      />
    </svg>
    <div
      v-if="state === 'disconnected'"
      class="absolute text-pale-dawn-semidark text-4xl bottom-[0.8rem] left-[-0.6rem]"
    >
      <FontAwesomeIcon icon="times" />
    </div>
    <div class="absolute top-24 text-center w-full align-center space-y-6">
      <div class="text-xl font-bold">{{ name }}</div>
      <div>{{ stateLabel }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";

import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { library } from "@fortawesome/fontawesome-svg-core";
import { faTimes } from "@fortawesome/free-solid-svg-icons";
library.add(faTimes);

const props = defineProps<{
  name?: string;
  state?: "disconnected" | "connecting" | "ready" | "reading";
}>();

const stateLabel = computed(() => {
  if (!props.state) {
    return "No Station";
  }
  return {
    disconnected: "Disconnected",
    connecting: "Connecting…",
    ready: "Ready",
    reading: "Reading…",
  }[props.state];
});
</script>

<style scoped>
@keyframes flow {
  from {
    stroke-dashoffset: 6px;
  }
  to {
    stroke-dashoffset: 0px;
  }
}

.data-flow {
  stroke-linecap: round;
  fill: none;
  stroke-dasharray: 0, 6;
  animation: 500ms linear infinite flow;
}
</style>
