<script>
import VerticalNavbar from './components/VerticalNavbar.vue'
import HorizontalNavbar from './components/HorizontalNavbar.vue'

export default {
  name: "app",
  components: {
    VerticalNavbar,
    HorizontalNavbar
  }
}
</script>


<template>
  <div class="'container'">
    <header class="navbar vertical">
        <VerticalNavbar/>
    </header>
    <header class="navbar horizontal">
        <HorizontalNavbar/>
    </header>
    <main class="content">
      <router-view/>
    </main>
  </div>
</template>


<style>
:root {
  --widthVerticalNav: 220px ;
  --heightHorizontalNav: 80px ;
  --colorBlack: #2a2438 ;
  --colorDesert: #cdc3ac ;
  --colorDesertDark: #beb59f ;
  --colorDesertDarkDark: #ada590 ;
  --colorDesertLight: #f3e7cc ;
  --colorTurquoise: #438E96 ;
  --colorMustard: #BFB98A ;
  --colorIvory: #FFFFF0;
}
body {
    margin: 0;
}
.container {
  display: flex;
  background-color: greenyellow;
  height: 100%;
}
.navbar {
  position: fixed;
}
.horizontal {
  background-color: aqua;
  top: 0;
  left: var(--widthVerticalNav);
  height: var(--heightHorizontalNav);
  width: 100%;
}
.vertical {
  background-color: aquamarine;
  top: 0;
  left: 0;
  height: 100vh;
  width: var(--widthVerticalNav);
}
.content {
  background-color: blanchedalmond;
  margin-left: var(--widthVerticalNav);
  margin-top: var(--heightHorizontalNav);
}
</style>