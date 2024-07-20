<template>
  <div>
    {{ id }}
    <LineGraph/>
  </div>
</template>

<script>
import LineGraph from '../../components/LineGraph.vue'

export default {
  components: {LineGraph},
  props: ['id'],
}
</script>

<style scoped>
div {
  height: 30rem;
  width: 50%;
  background-color: azure;
}
</style>