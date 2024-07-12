import Vue from "vue"
import App from "./App.vue"
import router from "./router"
import store from "./store"
import vuetify from "./plugins/vuetify"
import notifier from "./plugins/notifier"

Vue.config.productionTip = false

Vue.use(notifier)

Number.prototype.map = function(in_min, in_max, out_min, out_max) {
    return ((this - in_min) * (out_max - out_min)) / (in_max - in_min) + out_min
}

new Vue({
    router,
    store,
    vuetify,
    render: h => h(App)
}).$mount("#app")
