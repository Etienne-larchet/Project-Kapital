<template>
    <component :is="dynamicIcon"/>
  </template>
  
  <script>
  export default {
    name: 'DynamicIcon',
    props: {
      icon: {
        type: String,
        required: true,
      },
    },
    computed: {
      dynamicIcon () {
        return () => import(
          /* webpackChunkName: "icons" */
          /* webpackMode: "lazy-once" */ 
          `./icons/${this.icon}.svg`
        )
      },
    },
  }
  </script>