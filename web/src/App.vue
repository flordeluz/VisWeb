<template>
<v-app>
  <v-app-bar color="primary" app clipped-left>
    <v-toolbar-title class="white--text">
      <h1>{{ pageTitle }}</h1></v-toolbar-title>
    <v-spacer></v-spacer>
    <v-btn class="mr-2" href="/metadata" :elevated="isElevatedHome" :outlined="isOutlinedHome" color="white" @click="handleClick">Home</v-btn>
    <v-btn class="mr-2" href="/assets" id="dynAssets" :elevated="isElevatedAssets" :outlined="isOutlinedAssets" color="white">Assets</v-btn>
    <v-btn class="mr-2" href="/net" id="dynNet" :elevated="isElevatedNet" :outlined="isOutlinedNet" :disabled="buttonsDisabled" color="white">Navigation</v-btn>
    <v-btn class="mr-2" href="/visualize" id="dynVisualize" :elevated="isElevatedVisualize" :outlined="isOutlinedVisualize" :disabled="buttonsDisabled" color="white">Time Series</v-btn>
    <v-btn class="mr-2" href="/stats" id="dynStats" :elevated="isElevatedStats" :outlined="isOutlinedStats" :disabled="buttonsDisabled" color="white">Statistics</v-btn>
    <v-btn class="mr-2" href="/spiral" id="dynSpiral" :elevated="isElevatedSpiral" :outlined="isOutlinedSpiral" :disabled="buttonsDisabled" color="white">Spiral</v-btn>
  </v-app-bar>
  <!-- <v-navigation-drawer v-model="showSidebar" temporary fixed> -->
    <!--   <v-list nav> -->
      <!--     <v-list-item> -->
	<!--       <v-list-item-content class="my-2"> -->
	  <!--         <h1>GuiVisWeb</h1> -->
	  <!--       </v-list-item-content> -->
	<!--     </v-list-item> -->
      <!--     <v-divider></v-divider> -->
      <!--     <v-list-item-group ripple="true" class="mt-5"> -->
	<!--       <v-list-item> -->
	  <!--         <v-list-item-icon> -->
	    <!--           <v-icon>mdi-theme-light-dark</v-icon> -->
	    <!--         </v-list-item-icon> -->
	  <!-- 	  <v-list-item-title text @click="changeTheme"> -->
	    <!-- 	    Modo {{ this.darkMode ? "claro" : "oscuro" }} -->
	    <!-- 	  </v-list-item-title> -->
	  <!--       </v-list-item> -->
	<!--     </v-list-item-group> -->
      <!--   </v-list> -->
    <!-- </v-navigation-drawer> -->
  <v-main>
    <router-view></router-view>
  </v-main>
  <v-dialog v-model="exitdl" max-width="400">
    <v-card>
      <v-card-title class="headline">Export your data first</v-card-title>
      <v-card-text>
	All changes in your data will be lost. Do you want to continue?
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <!-- Cancel button -->
        <v-btn color="secondary" @click="exitdl = false">
          Cancel
        </v-btn>
        <!-- Confirm button -->
        <v-btn color="primary" @click="confirmExit">
          Confirm
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</v-app>
</template>

<script>
// -*- mode: JavaScript -*-
import { AppBus } from './appBus';

export default {
    name: "App",
    components: {},
    data: () => ({
	// darkMode: false,
	// showSidebar: null,
	// openModal: false,
	// searchData: "",
	// mode: "ts",
	exitdl: false,
	dataChanged: false,
	buttonsDisabled: true,
	isElevatedHome: true,
	isOutlinedHome: false,
	isElevatedAssets: false,
	isOutlinedAssets: true,
	isElevatedNet: false,
	isOutlinedNet: true,
	isElevatedVisualize: false,
	isOutlinedVisualize: true,
	isElevatedStats: false,
	isOutlinedStats: true,
	isElevatedSpiral: false,
	isOutlinedSpiral: true
    }),
    computed: {
	pageTitle: function() {
	    console.log("[ Page title ]:", this.$route.name)
	    return this.$route.name === "Spiral" ? "VisCyclic" : "GuiVisWeb"
	}
    },
    mounted: function() {
	const savedDataChanged = localStorage.getItem('dataChanged');
	if (savedDataChanged !== null) {
	    this.dataChanged = JSON.parse(savedDataChanged);
	}
	if (window.location.pathname === "/") {
	    this.$router.push("/metadata")
	}
    },
    created: function() {
	AppBus.$on('disabled-buttons', (state) => {
	    this.buttonsDisabled = state;
	});
	AppBus.$on('update-button-home', (elevated, outlined) => {
	    this.isElevatedHome = elevated;
	    this.isOutlinedHome = outlined;
	});
	AppBus.$on('update-button-assets', (elevated, outlined) => {
	    this.isElevatedAssets = elevated;
	    this.isOutlinedAssets = outlined;
	});
	AppBus.$on('update-button-net', (elevated, outlined) => {
	    this.isElevatedNet = elevated;
	    this.isOutlinedNet = outlined;
	});
	AppBus.$on('update-button-visualize', (elevated, outlined) => {
	    this.isElevatedVisualize = elevated;
	    this.isOutlinedVisualize = outlined;
	});
	AppBus.$on('update-button-stats', (elevated, outlined) => {
	    this.isElevatedStats = elevated;
	    this.isOutlinedStats = outlined;
	});
	AppBus.$on('update-button-spiral', (elevated, outlined) => {
	    this.isElevatedSpiral = elevated;
	    this.isOutlinedSpiral = outlined;
	});
	AppBus.$on('data-changed', (waschanged) => {
	    this.dataChanged = waschanged;
	    localStorage.setItem('dataChanged', JSON.stringify(waschanged));
	});
    },
    beforeDestroy: function() {
	AppBus.$off('disabled-buttons');
	AppBus.$off('update-button-home');
	AppBus.$off('update-button-assets');
	AppBus.$off('update-button-net');
	AppBus.$off('update-button-visualize');
	AppBus.$off('update-button-stats');
	AppBus.$off('update-button-spiral');
	AppBus.$off('data-changed');
    },
    methods: {
	handleClick(event) {
	    if (this.dataChanged) {
		event.preventDefault();
		this.exitdl = true;
	    }
	},
	confirmExit() {
	    this.exitdl = false;
	    localStorage.setItem('dataChanged', JSON.stringify(false));
	    window.location.href = "/metadata";
	},
    }
}
</script>
