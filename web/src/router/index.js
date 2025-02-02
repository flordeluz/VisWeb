import Vue from "vue"
import VueRouter from "vue-router"

Vue.use(VueRouter)

const routes = [
    {
	path: "/",
	name: "Home",
	component: () => import("../views/Home.vue")
    },
    {
	path: "/spiral/:dataset/:station",
	name: "Spiral",
	component: () => import("../views/Spiral.vue"),
	meta: {
	    reload: true
	}
    },
    {
	path: "/stats/:dataset/:station",
	name: "Statistics",
	component: () => import("../views/Stats.vue"),
	meta: {
	    reload: true
	}
    },
    {
	path: "/net/:dataset/:station",
	name: "Network",
	component: () => import("../views/Network.vue"),
	meta: {
	    reload: true
	}
    },
    {
	path: "/visualize/:dataset/:station",
	name: "Visualize Database",
	component: () => import("../components/TimeSeries.vue"),
	meta: {
	    reload: true
	}
    },
    {
	path: "/metadata",
	name: "Database data",
	component: () => import("../views/MetaData.vue"),
	meta: {
	    reload: true
	}
    },
    {
	path: "/assets",
	name: "Import data",
	component: () => import("../views/Assets.vue"),
	meta: {
	    reload: true
	}
    },
    {
	path: "/assets/:dataset/:station",
	name: "Import and Export data",
	component: () => import("../views/Assets.vue"),
	meta: {
	    reload: true
	}
    }    
]

const router = new VueRouter({
    mode: "history",
    base: process.env.BASE_URL,
    routes
})

export default router
