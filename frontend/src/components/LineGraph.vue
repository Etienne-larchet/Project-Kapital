<template>
    <Line :data="chartData" :options="options"/>
  </template>
  
  <script>
  import { Line } from 'vue-chartjs'
  import { Chart as ChartJS, CategoryScale, LinearScale, LineElement, PointElement, Title, Tooltip, Legend} from 'chart.js'
  
  ChartJS.register( CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend)
  
  export default {
    name: 'LineChart',
    components: { Line },
    data() {
      return {
        chartData: {
          labels: [ 'January', 'February', 'March', 'April', 'May', 'June', 'July' ],
          datasets: [
            {
                label: 'My First Dataset',
                data: [65, 59, 80, 81, null, 30, 55],
                fill: false,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            },
            {
                label: 'My second Dataset',
                data: [30, 50, 80, 90, 0, 20],
                fill: true,
                borderColor: 'rgb(192, 192, 192)',
                tension: 0.3
            }
        ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
        }
      }
    }
  }
  </script>