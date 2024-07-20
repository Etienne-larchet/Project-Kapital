import { createRouter, createWebHistory } from 'vue-router'
import Overview from '../views/Overview.vue'
import Portfolios from '../views/portfolios/Portfolios.vue'
import PortfolioDetails from '../views/portfolios/PortfolioDetails.vue'
import Analysis from '../views/Analysis.vue'
import Simulations from '../views/Simulations.vue'
import Budget from '../views/Budget.vue'
import Forecasts from '../views/Forecasts.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'overview',
      component: Overview 
    },
    {
      path: '/portfolios',
      name: 'portfolios',
      component: Portfolios 
    },
    {
      path: '/portfolios/:id',
      name: 'PortfolioDetails',
      component: PortfolioDetails,
      props: true,
    },
    {
      path: '/analysis',
      name: 'analysis',
      component: Analysis 
    },
    {
      path: '/simulations',
      name: 'simulations',
      component: Simulations 
    },
    {
      path: '/budget',
      name: 'budget',
      component: Budget 
    },
    {
      path: '/forecasts',
      name: 'forecasts',
      component: Forecasts 
    },
  ]
})

export default router
