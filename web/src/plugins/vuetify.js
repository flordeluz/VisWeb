import Vue from "vue"
import Vuetify from "vuetify/lib/framework"

Vue.use(Vuetify)

export default new Vuetify({
    theme: {
	options: {
	    customProperties: true
	},
	themes: {
	    // light: {
	    //   primary: "#8bc34a",
	    //   secondary: "#3f51b5",
	    //   accent: "#ff5722",
	    //   error: "#f44336",
	    //   warning: "#ffc107",
	    //   info: "#009688",
	    //   success: "#2196f3"
	    // }
	}
    }
})
