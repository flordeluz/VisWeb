import Vue from "vue"
import Vuex from "vuex"

Vue.use(Vuex)

export default new Vuex.Store({
    state: {
	messageHandler: {
	    message: "",
	    color: "info"
	},
	gradesHandler: {}
    },
    mutations: {},
    actions: {},
    modules: {}
})
