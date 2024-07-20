<script>
import overviewIcon from './icons/overviewIcon.svg';
import portfoliosIcon from './icons/portfoliosIcon.svg';
import analysisIcon from './icons/analysisIcon.svg';
import simulationsIcon from './icons/simulationsIcon.svg';
import budgetIcon from './icons/budgetIcon.svg';
import forecastsIcon from './icons/forecastsIcon.svg';

export default {
    name: 'vertical-navbar',
    components: {},
    data () {
        return {
            menuItems: [
                {name: 'Vue Global', id:0, link:'/', icon: overviewIcon},
                {name: 'Portefeuilles', id:1, link:'/portfolios', icon:portfoliosIcon, subItems: [{name:'ptf1', id: '01'}, {name:'ptf2', id: '02'}], isHidden: true},
                {name: 'Analyse', id:2, link:'/analysis', icon:analysisIcon},
                {name: 'Simulations', id:3, link:'/simulations', icon:simulationsIcon},
                {name: 'Budget', id:4, link:'/budget', icon:budgetIcon},
                {name: 'Prévisions', id:5, link:'/forecasts', icon: forecastsIcon},
            ]
        }
    },
}
</script>


<template>
    <aside class="vertical-navbar">
        <div class="headnav section">
            <span id="logo">Kapital</span>
        </div>
        <nav class="menu section">
            <router-link v-for="item in menuItems" :key="item.id" :to="item.link" style="text-decoration: None;">
                <div class="item" @click="item.isHidden = !item.isHidden">
                    <img :src="item.icon" :alt="item.name"/>
                    <span class="itemName">{{ item.name }}</span> 
                    <div class="subMenu" v-if="item.subItems && !item.isHidden">
                        <router-link v-for="subItem in item.subItems" :key="subItem.id" class="subItemName" :to="{name:'PortfolioDetails', params: {id: subItem.id}}">
                            <span>{{ subItem.name }}</span>
                        </router-link>
                    </div>
                </div>
            </router-link>
        </nav>
        <div class="account section">
            this is account section
        </div>
    </aside>
</template>


<style scoped>
.vertical-navbar {
    box-sizing: border-box ;
    padding: 0.5rem 0.5rem 0 0.5rem ;
    background-color: var(--colorDesert) ;
    height: 100% ;
    display: flex ;
    flex-direction: column;
}
.section {
    padding: 0.5rem;
}
.headnav {
    height: 5rem;
    span {
        display: block;
        margin: 2rem 2rem;
        color: var(--colorBlack);
        font-weight: bold;
        font-size: 1.6rem;
    }
}
nav {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.3rem;
    user-select: none;

    .item {
        border-radius: 5px;
        padding: 5px 9px;
        display: flex;
        flex-flow: row wrap;
        transition: 0.2s ease-in-out;
        img {
            height: 32px;
        };
        .itemName {
            flex: 1;
            color: var(--colorBlack);
            text-transform: uppercase;
            margin: auto 0;
            margin-left: 7px;
        };
        .subMenu {
            flex: 1;
            margin: 0 0 0 40px;
            padding: 0;
        }
        .subItemName {
            display: flex;
            flex-direction: column;
            text-decoration: none;
            color: var(--colorBlack);
            padding: 3px 5px;
            border-radius: 3px;
            transition: 0.2s ease-in-out;
        }
        .subItemName:hover {
            background-color: var(--colorDesertDarkDark);
        }
    }
    .item:hover {
        background-color: var(--colorDesertDark);
        cursor: pointer;
    }
}
.account {
    background-color: var(--colorBlack);
    color: var(--colorIvory);
    height: 40px;
    border-radius: 5px 5px 2px 2px;
}
</style>