<template>
<v-container class="my-6" fluid>
  <div class="text-center load-layer" v-if="loading_data">
    <v-progress-circular :size="100" class="loader" color="primary" indeterminate>
      Loading data...
    </v-progress-circular>
  </div>
  <div class="text-center load-layer" v-if="executing_task">
    <v-progress-circular :size="100" class="loader" color="primary" indeterminate>
      Executing Task...
    </v-progress-circular>
  </div>
  <v-row dense align="center" justify="center" v-if="datasetSelected">
    <h2>Dataset: {{ dataset.toUpperCase() }}, Station: {{ station.toUpperCase() }}</h2>
  </v-row>
  <v-row dense align="center" justify="center" v-if="datasetSelected">
    <v-col cols="1">
      <!-- noop -->
    </v-col>
    <v-col cols="12">
      <div class="legend-tooltip" v-if="legendVisible">
	<div class="legend-item">
          <span class="dot redlg"></span> Pending activities
	</div>
	<div class="legend-item">
          <span class="dot bluelg"></span> Applied activities
	</div>
	<div class="legend-item">
          <span class="dot graylg"></span> Not ready yet due to pending
	</div>
	<div class="legend-item">
          <span class="dot greenlg"></span> No more actions needed
	</div>
	<div class="legend-item">
          <span class="dot orangelg"></span> Optional activities
	</div>
      </div>      
      <div v-html="rawcontainer"></div>
      <div class="tooltip" v-if="tooltipVisible">
	{{ tooltipText }}
      </div>
    </v-col>
    <v-col cols="1">
      <!-- noop -->
    </v-col>
  </v-row>
  <v-dialog v-model="dialog" width="500">
    <v-card mt="4">
      <v-card-title class="headline grey lighten-2">
        Microtask Parameter
      </v-card-title>
      <v-card-text>
        <v-container>
          <v-form ref="parameters_form">
            <v-row align="center" justify="center">
              <v-col>
                <v-text-field label="List of features (comma-separated)" v-model="n_comp" ref="n_comp"
			      v-if="main_operation === 'reduce'" :rules="[v => !!v || 'At least one feature to drop']" />
                <v-text-field label="Transform factor" v-model="factor" ref="factor"
			      v-if="main_operation === 'transform'" :rules="[v => !!v || 'Required']" />
                <!-- <v-select label="Feature" v-model="feature" -->
		<!-- 	  :items="[ -->
		<!-- 		  { text: 'Precipitation', value: 0 }, -->
		<!-- 		  { text: 'Temp Max', value: 1 }, -->
		<!-- 		  { text: 'Temp Min', value: 2 } -->
		<!-- 		  ]" -->
		<!-- 	  ref="feature" v-if="main_operation === 'trend' || -->
		<!-- 			      main_operation === 'seasonality' || -->
		<!-- 			      main_operation === 'cyclicity'" -->
		<!-- 	  :rules="[v => !!v || 'Required']" /> -->
              </v-col>
              <v-col>
                <v-btn @click="execActivityParams" large color="primary">
                  Apply</v-btn>
              </v-col>
            </v-row>
          </v-form>
        </v-container>
      </v-card-text>
    </v-card>
  </v-dialog>
  <v-dialog v-model="seasdl" width="800">
    <v-card mt="4">
      <v-card-title class="headline grey lighten-2">
        Seasonality
      </v-card-title>
      <!-- <v-img :src="seasim" :height="seashg" :width="seaswd"></v-img> -->
      <div v-html="vseason"></div>
    </v-card>
  </v-dialog>
  <v-dialog v-model="trendl" width="800">
    <v-card mt="4">
      <v-card-title class="headline grey lighten-2">
        Trend
      </v-card-title>
      <!-- <v-img :src="trenim" :height="trenhg" :width="trenwd"></v-img> -->
      <div v-html="vtrend"></div>
    </v-card>
  </v-dialog>
  <v-dialog v-model="noisdl" width="800">
    <v-card mt="4">
      <v-card-title class="headline grey lighten-2">
        Noise
      </v-card-title>
      <!-- <v-img :src="noisim" :height="noishg" :width="noiswd"></v-img> -->
      <div v-html="vnoise"></div>
    </v-card>
  </v-dialog>
</v-container>
</template>

<script>
// -*- mode: JavaScript -*-
import EdgeCurveProgram from "@sigma/edge-curve";
// import { createNodeImageProgram } from "@sigma/node-image";
import Graph from "graphology";
// Available layouts
//* import ForceLayout from "graphology-layout-force/worker";
// import ForceLayout from "graphology-layout-forceatlas2/worker";
// import ForceLayout from "graphology-layout-noverlap/worker";

import Sigma from "sigma";

import { onStoryDown } from "./utils";
import NodeGradientProgram from "./node-gradient";

import axios from "axios"
import "@/views/bootstrap.min.css"
const vcteicon = "iVBORw0KGgoAAAANSUhEUgAAAYAAAAGACAYAAACkx7W/AAABJGVYSWZJSSoACAAAAAsAAAEEAAEAAACAAQAAAQEEAAEAAACAAQAAAgEDAAMAAACSAAAADgECABoAAACYAAAAEgEDAAEAAAABAAAAGgEFAAEAAACyAAAAGwEFAAEAAAC6AAAAKAEDAAEAAAADAAAAMQECAA0AAADCAAAAMgECABQAAADQAAAAaYcEAAEAAADkAAAAAAAAAAgACAAIAFZDIFRlY2gKQXJ0LiBWaWN0b3IgU2FsYXMANwIAABQAAAA3AgAAFAAAAEdJTVAgMi4xMC4zOAAAMjAyNDowNzoyNCAxNjozMDo1MgACAIaSBwAhAAAAAgEAAAGgAwABAAAAAQAAAAAAAAAAAAAAAAAAAFZDIFRlY2gKQXJ0LiBWaWN0b3IgU2FsYXMAaGtkVgAAAYRpQ0NQSUNDIHByb2ZpbGUAAHicfZE9SMNAHMVfW6UiFQUrFOmQoTrZRUUcaxWKUCHUCq06mFz6BU0akhQXR8G14ODHYtXBxVlXB1dBEPwAcXZwUnSREv+XFFrEeHDcj3f3HnfvAH+zylSzJwGommVkUkkhl18Vgq8IIoIRRDEkMVOfE8U0PMfXPXx8vYvzLO9zf44BpWAywCcQJ5huWMQbxDObls55nzjMypJCfE48YdAFiR+5Lrv8xrnksJ9nho1sZp44TCyUuljuYlY2VOJp4piiapTvz7mscN7irFbrrH1P/sJQQVtZ5jrNKFJYxBJECJBRRwVVWIjTqpFiIkP7SQ//qOMXySWTqwJGjgXUoEJy/OB/8Ltbszg16SaFkkDvi21/jAHBXaDVsO3vY9tunQCBZ+BK6/hrTWD2k/RGR4sdAYPbwMV1R5P3gMsdIPKkS4bkSAGa/mIReD+jb8oDw7dA/5rbW3sfpw9AlrpK3wAHh8B4ibLXPd7d193bv2fa/f0Ajd9ysblMNEcAAA14aVRYdFhNTDpjb20uYWRvYmUueG1wAAAAAAA8P3hwYWNrZXQgYmVnaW49Iu+7vyIgaWQ9Ilc1TTBNcENlaGlIenJlU3pOVGN6a2M5ZCI/Pgo8eDp4bXBtZXRhIHhtbG5zOng9ImFkb2JlOm5zOm1ldGEvIiB4OnhtcHRrPSJYTVAgQ29yZSA0LjQuMC1FeGl2MiI+CiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPgogIDxyZGY6RGVzY3JpcHRpb24gcmRmOmFib3V0PSIiCiAgICB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIKICAgIHhtbG5zOnN0RXZ0PSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAvc1R5cGUvUmVzb3VyY2VFdmVudCMiCiAgICB4bWxuczpHSU1QPSJodHRwOi8vd3d3LmdpbXAub3JnL3htcC8iCiAgICB4bWxuczpkYz0iaHR0cDovL3B1cmwub3JnL2RjL2VsZW1lbnRzLzEuMS8iCiAgICB4bWxuczp0aWZmPSJodHRwOi8vbnMuYWRvYmUuY29tL3RpZmYvMS4wLyIKICAgIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIKICAgeG1wTU06RG9jdW1lbnRJRD0iZ2ltcDpkb2NpZDpnaW1wOmZmMmJhOWU3LTIyNjItNGU5Ni04OTZlLTBkN2M5OTU0NTEwMiIKICAgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDo3NGRjZGFlYi0zZjZjLTQ1NjEtODE5ZS01Zjk2ZGRkMzE1MmUiCiAgIHhtcE1NOk9yaWdpbmFsRG9jdW1lbnRJRD0ieG1wLmRpZDpiZWRjZTY4Ni0wOGI2LTQyZDEtYmQ2OS1jNjA0YTU2N2E0NmYiCiAgIEdJTVA6QVBJPSIyLjAiCiAgIEdJTVA6UGxhdGZvcm09IkxpbnV4IgogICBHSU1QOlRpbWVTdGFtcD0iMTcyMTg1NjY1NDY0MTI2NSIKICAgR0lNUDpWZXJzaW9uPSIyLjEwLjM4IgogICBkYzpGb3JtYXQ9ImltYWdlL3BuZyIKICAgdGlmZjpPcmllbnRhdGlvbj0iMSIKICAgeG1wOkNyZWF0b3JUb29sPSJHSU1QIDIuMTAiCiAgIHhtcDpNZXRhZGF0YURhdGU9IjIwMjQ6MDc6MjRUMTY6MzA6NTItMDU6MDAiCiAgIHhtcDpNb2RpZnlEYXRlPSIyMDI0OjA3OjI0VDE2OjMwOjUyLTA1OjAwIj4KICAgPHhtcE1NOkhpc3Rvcnk+CiAgICA8cmRmOlNlcT4KICAgICA8cmRmOmxpCiAgICAgIHN0RXZ0OmFjdGlvbj0ic2F2ZWQiCiAgICAgIHN0RXZ0OmNoYW5nZWQ9Ii8iCiAgICAgIHN0RXZ0Omluc3RhbmNlSUQ9InhtcC5paWQ6ZTAzOWYzNzEtYzAxOC00ODMyLWI2MjQtM2M5MWVjMDM3YzI3IgogICAgICBzdEV2dDpzb2Z0d2FyZUFnZW50PSJHaW1wIDIuMTAgKExpbnV4KSIKICAgICAgc3RFdnQ6d2hlbj0iMjAyNC0wNy0yNFQxNjozMDo1NC0wNTowMCIvPgogICAgPC9yZGY6U2VxPgogICA8L3htcE1NOkhpc3Rvcnk+CiAgPC9yZGY6RGVzY3JpcHRpb24+CiA8L3JkZjpSREY+CjwveDp4bXBtZXRhPgogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgIAogICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgCiAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAgICAKICAgICAgICAgICAgICAgICAgICAgICAgICAgCjw/eHBhY2tldCBlbmQ9InciPz46DYRFAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAB3RJTUUH6AcYFR42EFhb8gAAACF0RVh0Q29tbWVudABWQyBUZWNoCkFydC4gVmljdG9yIFNhbGFzaGEtCAAAIABJREFUeNrt3Xl0XOWZJ/7ve2/d2lWlXd73hdjgBcweg1kcjB1I0lk7C52ZJCQz3T3pNeTXmdPndJ+TmUxPTzqdIZ2ETkLINknoEFbZ2BhMIBiwWWxigzHe5N2ytauq7va+vz9u3dKtUlWpJC/Y8vfDKUoqyVLpVt3ned/nXS5AREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREQ0/gkeAhpP9uzZo7mu25hMJidrmjbdMIypQojJmqY1CyEahBApIUQUQByAkf9nNoCMUiqnlOpTSnVLKU8qpQ7btn1QSnlgYGDgsK7rXbNnz5Y8ysQEQPQu27p1q97Q0DAjFostDYfDV+q6vkjTtAWGYbRqmhbVdR1CiMINQOG+EqVU4d6/ua4LKWXOtu0TUsqdrututyxrSzabfa27u3v/smXLXL4axARAdBY99dRTYsaMGTOTyeRNhmHcEgqFrguFQlMMw9A1TYOmaSMG+NOllIKUElJK2LbtOo5zyHGcF2zb3jgwMPDM/v379916662KrxYxARCdpueeey40ZcqUxdFo9EOGYdwRiUQWhMPhkK7r5yTg15oQXNeFZVmOaZo7bdt+LJfL/fbQoUPbli9f7vBVJCYAohpt2rRJtLS0zE2n05+KRCIfi0aj88PhsAiFQtA07bx+7lJKOI4Dy7JULpfbZZrmr3t7e3/e2dm5e8WKFewZEBMAUTnbtm2LJZPJO+Px+N2xWGx5JBIxDMM4L1r6Y+0Z2LYN0zTtbDb7XCaTuW9gYODRxYsXZ/lqExMAkRf4W9Lp9OdjsdiXYrHYtEgkgguhtT/aXoFpmshmsx3ZbPZ7vb29P1i8eHEnX31iAqCL0pYtWyY2NTX9RSKR+EI8Hm/wA/+F1tofTa/ATwSZTKZ7cHDw30+dOvWtK6+88ijfDcQEQBdLi78pHo//VTKZ/NNEIpEeby3+0fQIBgcHewcGBr6TyWS+uXjx4lN8dxATAI1Lzz//fKSxsfHuVCr1tUQi0RaNRhEOhy+awF8uEViW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973vfZFQKHS3pmlfE0K0jeqNWhLoR9omorT8czo9gNKPR9ruody1kmsI/MellF93HOe+9evX89q9xARA49Ptt9/epGnaXwkh/lQIkR7TGzcQ0Ec7IFxDMK5a9ikN/qW9h1EG/l6l1HeklN9cu3btKb47iAmALpYewUTDMP5CCPEFIUTDGXlDV2j9j6UEVKkXcCYopbqVUv9u2/a31q9ff5TvBmICoIvSqlWrWkKh0OcBfEkIMW08/61KqQ4A33Mc5wfr1q3jAC8xARDlE0FM1/U7hRB3CyGWAzDGyZ9mK6WeU0rd57ruo+vWrcvy1SYmAKIybrnlFmEYxtxQKPQpAB8TQsy/AN+rSim1C8CvHcf5uW3buzdu3MhZPcQEQDSKZBCKRqOLhRAfAnCHEGIBgNB5+nQdpdROAI8ppX6by+W2bdy40eGrSEwARKdpxYoVIh6Pz9Q07SYhxC0ArgMwBTUsMDtLXACHALyglNoopXwmk8ns27RpE1v6xARAdDatXLlSD4VCMzRNWyqEuBLAIgALhBCtAKJn+NfllFInAOwEsF0ptUVK+ZrjOPs3bNjg8tUgJgCid9nq1as1pVSjruuTAUwXQkxVSk0WQjQDaACQyieHOIYGmW0AGQA5AH0AupVSJ4UQh5VSBwEccF33sBCiq729XfIoExEREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREREV04/n+adKeT0DF0KAAAAABJRU5ErkJggg=="
export default {
    name: "Network",
    data: () => ({
	dataset: "",
	station: null,
	datasetSelected: false,
	// rawcontainer: '<div id="container" style="width: 100vh; height: 80vh; background: #fff;"></div>',
	rawcontainer: '<div id="container" style="height: 80vh; width: 1080px; background: #fff;"></div>',
	container: null,
	graph: null,
	renderer: null,
	layout: null,
	loading_data: true,
	executing_task: false,
	dialog: false,
	seasdl: false,
	// seasim: "",
	// seashg: 500,
	// seaswd: 300,
	vseason: '<img src="data:image/png;base64,' + vcteicon + '">',
	trendl: false,
	// trenim: "",
	// trenhg: 500,
	// trenwd: 300,
	vtrend: '<img src="data:image/png;base64,' + vcteicon + '">',
	noisdl: false,
	// noisim: "",
	// noishg: 500,
	// noiswd: 300,
	vnoise: '<img src="data:image/png;base64,' + vcteicon + '">',
	n_comp: "",
	factor: 1,
	main_operation: "",
	main_path: "",
	RED: "#FA4F40", // ACTION Enabler
	ORANGE: "#FF6600", // ACTION Enabler
	BLUE: "#727EE0", // ACTION Enabler
	LIGHTBLUE: "#3399f8",
	GREEN: "#5DB346",
	YELLOW: "#F6F606",
	GRAY: "#767686",
	BLACK: "#000000",
	PROCSZ: 32, // Process
	SUBPSZ: 16, // Subprocess
	ACTVSZ: 8, // Activity in ACTION
	PROCCO: { // Default color GRAY
            "Data Quality": "#767686",
	    "Data Reduction": "#767686",
            "Variables Behavior": "#767686"
	},
	PROCPR: { // prio
            "Data Quality": 1,
	    "Data Reduction": 2,
            "Variables Behavior": 3
	},
	PROCBY: [], // bypass
	SUBPCO: { // Default color GRAY
	    "Data Quality": {
		"Clean": "#767686",
		"Nulls": "#767686",
		"Outliers": "#767686",
		"Normalize": "#767686",
		"Transform": "#767686"
	    },
	    "Data Reduction": {
		"DimRed": "#767686"
	    },
	    // "Variables Behavior": {
	    // 	"Trend": "#767686",
	    // 	"Seasonality": "#767686",
	    // 	"Cyclicity": "#767686"
	    // }
	    "Variables Behavior": {
		"Analysis": "#767686"
	    }
	},
	SUBPPR: { // prio
	    "Data Quality": {
		"Clean": 11,
		"Nulls": 12,
		"Outliers": 13,
		"Normalize": 14,
		"Transform": 15
	    },
	    "Data Reduction": {
		"DimRed": 21
	    },
	    // "Variables Behavior": {
	    // 	"Trend": 31,
	    // 	"Seasonality": 32,
	    // 	"Cyclicity": 33
	    // }
	    "Variables Behavior": {
		"Analysis": 31
	    }
	},
	SUBPBY: [], // bypass
	ACTVCO: { // Default color GRAY
	    "Data Quality": {
		"Clean": {
		},
		"Nulls": {
		    "Rolling Mean": "#767686",
		    "Decision Tree": "#767686",
		    "Stochastic Gradient": "#767686",
		    "Locally Weighted": "#767686",
		    "Legendre": "#767686",
		    "Random Forest": "#767686",
		    "KNN": "#767686"
		},
		"Outliers": {
		    "Interquartile Range": "#767686",
		    "Z-Score": "#767686"
		},
		"Normalize": {
		    "MinMax": "#767686",
		    "Standard": "#767686",
		    "MaxAbs": "#767686",
		    "Robust": "#767686"
		},
		"Transform": {
		    "Linear": "#767686",
		    "Quadratic": "#767686",
		    "Square Root": "#767686",
		    "Logarithm": "#767686",
		    "Differencing": "#767686"
		}
	    },
	    "Data Reduction": {
		"DimRed": {
		    "Factor Analysis": "#767686",
		    "PCA and correlation": "#767686"
		}
	    },
	    // "Variables Behavior": {
	    // 	"Trend": {
	    // 	},
	    // 	"Seasonality": {
	    // 	},
	    // 	"Cyclicity": {
	    // 	}
	    // }
	    "Variables Behavior": {
		"Analysis": {
		    "Trend": "#767686",
		    "Seasonality": "#767686",
		    "Cyclicity": "#767686",
		    "Noise": "#767686"
		}
	    }
	},
	ACTVPR: { // prio
	    "Data Quality": {
		"Clean": {
		},
		"Nulls": {
		    "Rolling Mean": 121,
		    "Decision Tree": 122,
		    "Stochastic Gradient": 123,
		    "Locally Weighted": 124,
		    "Legendre": 125,
		    "Random Forest": 126,
		    "KNN": 127
		},
		"Outliers": {
		    "Interquartile Range": 131,
		    "Z-Score": 132
		},
		"Normalize": {
		    "MinMax": 141,
		    "Standard": 142,
		    "MaxAbs": 143,
		    "Robust": 144
		},
		"Transform": {
		    "Linear": 151,
		    "Quadratic": 152,
		    "Square Root": 153,
		    "Logarithm": 154,
		    "Differencing": 155
		}
	    },
	    "Data Reduction": {
		"DimRed": {
		    "Factor Analysis": 211,
		    "PCA and correlation": 212
		}
	    },
	    // "Variables Behavior": {
	    // 	"Trend": {
	    // 	},
	    // 	"Seasonality": {
	    // 	},
	    // 	"Cyclicity": {
	    // 	}
	    // }
	    "Variables Behavior": {
		"Analysis": {
		    "Trend": 311,
		    "Seasonality": 312,
		    "Cyclicity": 313,
		    "Noise": 314
		}
	    }
	},
	ACTVBY: [],
	guide: [
	    {
		ref: "Data Quality",
		text: "Ensuring data is accurate, complete, and reliable for analysis and decision-making."
	    },
	    {
		ref: "Cleaning",
		text: "The process of removing or correcting inaccurate, corrupted, or incomplete data."
	    },
	    {
		ref: "Nulls treatment",
		text: "Handling missing values in a dataset using methods like imputation or deletion."
	    },
	    {
		ref: "Rolling Mean",
		text: "A technique to smooth out short-term fluctuations and highlight trends over time."
	    },
	    {
		ref: "Decision Tree",
		text: "A supervised learning model used for classification and regression tasks."
	    },
	    {
		ref: "Stochastic Gradient",
		text: "An optimization method that updates model parameters using a randomly selected subset of data."
	    },
	    {
		ref: "Locally Weighted",
		text: "A non-parametric regression method that uses nearby points for making predictions."
	    },
	    {
		ref: "Random Forest",
		text: "An ensemble learning method using multiple decision trees to improve accuracy."
	    },
	    {
		ref: "Legendre",
		text: "A type of polynomial used in approximation and solving differential equations."
	    },
	    {
		ref: "kNN",
		text: "A non-parametric algorithm that classifies data based on the closest training examples."
	    },
	    {
		ref: "Outliers",
		text: "Data points that significantly differ from the rest of the dataset."
	    },
	    {
		ref: "Interquartile Range",
		text: "A measure of statistical dispersion, calculated as the difference between the upper and lower quartiles."
	    },
	    {
		ref: "Z-Score",
		text: "A statistical measure that describes a value's relationship to the mean of a group of values."
	    },
	    {
		ref: "Normalization",
		text: "The process of scaling data to fit within a specific range, usually [0, 1]."
	    },
	    {
		ref: "Standard",
		text: "Scaling data to have a mean of 0 and a standard deviation of 1."
	    },
	    {
		ref: "MinMax",
		text: "A normalization technique that scales data to a fixed range, typically [0, 1]."
	    },
	    {
		ref: "Robust",
		text: "A scaling method that uses the median and the interquartile range to scale features."
	    },
	    {
		ref: "MaxAbs",
		text: "A scaling method that scales each feature by its maximum absolute value."
	    },
	    {
		ref: "Transformations",
		text: "Techniques to convert data into a suitable format or scale for analysis."
	    },
	    {
		ref: "Differencing",
		text: "A technique used to remove trends or seasonality in time series data."
	    },
	    {
		ref: "Logarithm",
		text: "A transformation that helps to reduce skewness in data."
	    },
	    {
		ref: "Quadratic",
		text: "A transformation involving squaring data values to capture non-linear relationships."
	    },
	    {
		ref: "Square Root",
		text: "A transformation that helps to reduce skewness and variance in data."
	    },
	    {
		ref: "Linear",
		text: "A basic transformation where data is scaled linearly without any change in shape."
	    },
	    {
		ref: "Data Reduction",
		text: "Techniques to reduce the amount of data while retaining its essential information."
	    },
	    {
		ref: "Dimensionality Reduction",
		text: "The process of reducing the number of random variables under consideration."
	    },
	    {
		ref: "PCA and correlation",
		text: "It involves using the correlation with PCA to reduce dimensionality while accounting for variable relationships."
	    },
	    {
		ref: "Factor Analysis",
		text: "A statistical method used to describe variability among observed variables in terms of fewer unobserved variables."
	    },
	    {
		ref: "Variables Behavior",
		text: "Analyzing how different variables interact and change in response to each other."
	    },
	    {
		ref: "Decomposition Analysis",
		text: "Breaking down time series data into trend, seasonality, and residual components."
	    },
	    {
		ref: "Trend",
		text: "The long-term movement or direction in time series data."
	    },
	    {
		ref: "Seasonality",
		text: "Recurring patterns or cycles in data at regular intervals over time."
	    },
	    {
		ref: "Cyclicity",
		text: "Fluctuations in data with a regular periodicity longer than a year."
	    },
	    {
		ref: "Noise",
		text: "Random variability in data that cannot be attributed to any known cause."
	    }
	],
	currentGuide: -1,
	tooltipVisible: false,
	tooltipText: '',
	legendVisible: true
    }),
    methods: {
	async execActivity(event, itemType, item) {
	    if (event === "clickNode") {
		let label;
		let color;
		let size;
		let path;
		let x_i;
		let y_i;
		let action = false;
		if (item && itemType) {
		    if (itemType === "node") {
			label = this.graph.getNodeAttribute(item, "label");
			color = this.graph.getNodeAttribute(item, "color");
			size = this.graph.getNodeAttribute(item, "size");
			path = this.graph.getNodeAttribute(item, "path");
			x_i = this.graph.getNodeAttribute(item, "x");
			y_i = this.graph.getNodeAttribute(item, "y");
			if (label == "Seasonality" && (color == this.RED || color == this.ORANGE || color == this.BLUE) && size == this.ACTVSZ) {
			    let behavss = await axios.get(
				"http://localhost:8080/behavior/seasonality/" + this.dataset + "/" + this.station,
				{ crossdomain: true }
			    );
			    this.vseason = behavss.data.seasonality;
			    this.seasdl = true;
			} else if (label == "Trend" && (color == this.RED || color == this.ORANGE || color == this.BLUE) && size == this.ACTVSZ) {
			    let behavtr = await axios.get(
				"http://localhost:8080/behavior/trend/" + this.dataset + "/" + this.station,
				{ crossdomain: true }
			    );
			    this.vtrend = behavtr.data.trend;
			    this.trendl = true;
			} else if (label == "Noise" && (color == this.RED || color == this.ORANGE || color == this.BLUE) && size == this.ACTVSZ) {
			    let behavns = await axios.get(
				"http://localhost:8080/behavior/noise/" + this.dataset + "/" + this.station,
				{ crossdomain: true }
			    );
			    this.vnoise = behavns.data.noise;
			    this.noisdl = true;
			} else if (label == "Linear" && (color == this.RED || color == this.ORANGE || color == this.BLUE) && size == this.ACTVSZ) {
			    this.main_operation = "transform";
			    this.main_path = path; // "transform/linear/";
			    this.dialog = true;
			} else if (label == "PCA and correlation" && (color == this.RED || color == this.ORANGE || color == this.BLUE) && size == this.ACTVSZ) {
			    this.main_operation = "reduce";
			    this.main_path = path; // "reduce/manual/";
			    this.dialog = true;
			} else if ((color == this.RED || color == this.ORANGE || color == this.BLUE) && size == this.ACTVSZ) {
			    action = true;
			}
			console.log("[", event, "]:", itemType, label, x_i, y_i, "action:", action);
		    } else if (itemType === "edge") {
			label = this.graph.getEdgeAttribute(item, "label");
			console.log("[", event, "]:", itemType, label);
		    } else {
			console.log("[", event, "]:", itemType, "unhandled");
		    }
		}
		if (action) {
		    if (path.startsWith("/")) {
			location.href = `${path}/${this.dataset}/${this.station}`;
		    } else {
			this.executing_task = true;
			let req_string;
			req_string = `http://localhost:8080/op/${this.dataset}/${path}`;
			// this.history.push({
			// 	name: `${this.operation.method}-clean`,
			// 	aux: req_string
			// })
			console.log(req_string);
			let actionrc = await axios.get(req_string, { crossdomain: true });
			console.log(actionrc);
			this.executing_task = false;
			location.reload();
		    }
		}
	    } else {	
		console.log("[", event, "]:", "unhandled");
	    }
	},
	async execActivityParams() {
	    console.log("[ Action with params ]");
	    if (this.main_operation === "reduce" && this.n_comp === "") {
		this.$refs["n_comp"].validate(true);
		return;
	    }
	    if (this.main_operation === "transform" && this.factor === "") {
		this.$refs["factor"].validate(true);
		return;
	    }
	    if (this.main_operation === "reduce") this.main_path = this.main_path + this.n_comp;
	    if (this.main_operation === "transform") this.main_path = this.main_path + this.factor;
	    this.executing_task = true;
	    let req_string;
	    req_string = `http://localhost:8080/op/${this.dataset}/${this.main_path}`;
	    console.log(req_string);
	    let actionrc = await axios.get(req_string, { crossdomain: true });
	    console.log(actionrc);
	    this.executing_task = false;
	    this.dialog = false;
	    this.$refs["parameters_form"].reset();
	    location.reload();
	},
	async showNetwork() {
	    this.datasetSelected = true;
	    let steprc = await axios.get(
		"http://localhost:8080/recommendation/" + this.dataset + "/" + this.station,
		{ crossdomain: true }
	    );
	    let itrecommends = steprc.data[0];
	    let itextends = steprc.data[1];
	    let itpath = steprc.data[2];
	    console.log("[ It Recommends ]");
	    console.log("[ Made Path ]: ", itpath);
	    for (var process in itrecommends) {
		console.log("[ Process ]:", process);
		console.log("[ Subprocesses ]:", itrecommends[process]);
		console.log("[ Subprocess Excluded Activities ]:", itextends["Excluded Activities"]);
		this.PROCCO[process] = this.PROCPR[process] == 3 ? /* this.BLUE */ this.LIGHTBLUE : this.RED;
		this.PROCBY.push(this.PROCPR[process]);
		for (var prio_coloring_p in this.PROCPR) {
		    if (! this.PROCBY.includes(this.PROCPR[prio_coloring_p])) {
			if (this.PROCPR[prio_coloring_p] < this.PROCPR[process]) {
			    this.PROCCO[prio_coloring_p] = this.GREEN;
			    for (var prio_coloring_a in this.SUBPCO[prio_coloring_p]) {
				this.SUBPCO[prio_coloring_p][prio_coloring_a] = this.GREEN;
				for (var prio_coloring_b in this.ACTVCO[prio_coloring_p][prio_coloring_a]) {
				    this.ACTVCO[prio_coloring_p][prio_coloring_a][prio_coloring_b] = this.GREEN;
				}
			    }
			}
		    }
		}
		for (var subprocess in itrecommends[process]) {
		    // this.SUBPCO[process][itrecommends[process][subprocess]] = this.SUBPPR[process][itrecommends[process][subprocess]] > 30 ? this.BLUE : this.RED;
		    if ( this.SUBPPR[process][itrecommends[process][subprocess]] > 30 ) {
			this.SUBPCO[process][itrecommends[process][subprocess]] = /* this.BLUE */ this.LIGHTBLUE;
		    } else if ( this.SUBPPR[process][itrecommends[process][subprocess]] == 15 ) {
			this.SUBPCO[process][itrecommends[process][subprocess]] = this.ORANGE;
			if ( itrecommends[process].length == 1 ) {
			    this.PROCCO[process] = this.ORANGE;
			}
		    } else {
			this.SUBPCO[process][itrecommends[process][subprocess]] = this.RED;
		    }
		    this.SUBPBY.push(this.SUBPPR[process][itrecommends[process][subprocess]]);
		    for (var prio_coloring_s in this.SUBPPR[process]) {
			if (! this.SUBPBY.includes(this.SUBPPR[process][prio_coloring_s])) {
			    if (this.SUBPPR[process][prio_coloring_s] < this.SUBPPR[process][itrecommends[process][subprocess]]) {
				this.SUBPCO[process][prio_coloring_s] = this.GREEN;
				for (var inactv_s_g in this.ACTVCO[process][prio_coloring_s]) {
				    this.ACTVCO[process][prio_coloring_s][inactv_s_g] = this.GREEN;
				}
			    } else {
				this.SUBPCO[process][prio_coloring_s] = this.GRAY; // this.YELLOW;
				for (var inactv_s_y in this.ACTVCO[process][prio_coloring_s]) {
				    this.ACTVCO[process][prio_coloring_s][inactv_s_y] = this.GRAY; // this.YELLOW;
				}
			    }
			}
		    }
		    console.log("[ Activities ]:");
		    for (var inactv in this.ACTVCO[process][itrecommends[process][subprocess]]) {
			console.log(" ", inactv);
			if (typeof itextends["Excluded Activities"] !== "undefined" && itextends["Excluded Activities"].length > 0) {
			    if (itextends["Excluded Activities"].includes(inactv)) {
				this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.GREEN;
			    } else {
				this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.ACTVPR[process][itrecommends[process][subprocess]][inactv] > 300 ? this.BLUE : this.ORANGE;
				this.ACTVBY.push(this.ACTVPR[process][itrecommends[process][subprocess]][inactv]);
			    }
			} else {
			    if ( this.ACTVPR[process][itrecommends[process][subprocess]][inactv] > 300 ) {
				this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.BLUE;
			    } else if ( this.ACTVPR[process][itrecommends[process][subprocess]][inactv] % 150 < 10 ) {
				this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.ORANGE;
			    } else {
				this.ACTVCO[process][itrecommends[process][subprocess]][inactv] = this.RED;
			    }
			    this.ACTVBY.push(this.ACTVPR[process][itrecommends[process][subprocess]][inactv]);
			}
		    }
		}
	    }
	    if (typeof itextends["DimRed"] !== "undefined") {
		console.log(itextends["DimRed"]);
		const foundFA = itextends["DimRed"].find(item => item.includes("FA Dim.Reduction"));
		if (foundFA) {
		    const regex = /\[(.*?)\]/;
		    const matchFA = foundFA.match(regex);
		    if (matchFA) {
			const valuesFA = matchFA[1].split(',').map(item => item.trim().replace(/'/g, ''));
			console.log(valuesFA);
			this.n_comp = valuesFA.join(',');
			console.log(this.n_comp);
		    }
		}
		if (this.n_comp == "") {
		    const foundMC = itextends["DimRed"].find(item => item.includes("Multicollinearity Dim.Reduction"));
		    if (foundMC) {
			const regex = /\[(.*?)\]/;
			const matchMC = foundMC.match(regex);
			if (matchMC) {
			    const valuesMC = matchMC[1].split(',').map(item => item.trim().replace(/'/g, ''));
			    console.log(valuesMC);
			    this.n_comp = valuesMC.join(',');
			    console.log(this.n_comp);
			}
		    }
		}
		if (this.n_comp == "") {
		    const foundPR = itextends["DimRed"].find(item => item.includes("Pearson Dim.Reduction"));
		    if (foundPR) {
			const regex = /\[(.*?)\]/;
			const matchPR = foundPR.match(regex);
			if (matchPR) {
			    const valuesPR = matchPR[1].split(',').map(item => item.trim().replace(/'/g, ''));
			    console.log(valuesPR);
			    this.n_comp = valuesPR.join(',');
			    console.log(this.n_comp);
			}
		    }
		}
		if (this.n_comp == "") {
		    const foundSP = itextends["DimRed"].find(item => item.includes("Spearman Dim.Reduction"));
		    if (foundSP) {
			const regex = /\[(.*?)\]/;
			const matchSP = foundSP.match(regex);
			if (matchSP) {
			    const valuesSP = matchSP[1].split(',').map(item => item.trim().replace(/'/g, ''));
			    console.log(valuesSP);
			    this.n_comp = valuesSP.join(',');
			    console.log(this.n_comp);
			}
		    }
		}
		if (this.n_comp == "") {
		    const foundKN = itextends["DimRed"].find(item => item.includes("Kendall Dim.Reduction"));
		    if (foundKN) {
			const regex = /\[(.*?)\]/;
			const matchKN = foundKN.match(regex);
			if (matchKN) {
			    const valuesKN = matchKN[1].split(',').map(item => item.trim().replace(/'/g, ''));
			    console.log(valuesKN);
			    this.n_comp = valuesKN.join(',');
			    console.log(this.n_comp);
			}
		    }
		}
	    }
	    await new Promise(r => setTimeout(r, 2000));
	    this.container = document.getElementById("container");
	    console.log("[ Container ]:", this.container);
	    this.graph = new Graph();
	    
	    // Node processes
	    this.graph.addNode("Data Quality", { x: -130, y: 0, size: this.PROCSZ, label: "Data Quality", forceLabel: true, type: "gradient", color: this.PROCCO["Data Quality"] });
	    this.graph.addNode("Data Reduction", { x: 0, y: 0, size: this.PROCSZ, label: "Data Reduction", forceLabel: true, type: "gradient", color: this.PROCCO["Data Reduction"] });
	    this.graph.addNode("Variables Behavior", { x: 90, y: 0, size: this.PROCSZ, label: "Variables Behavior", forceLabel: true, type: "gradient", color: this.PROCCO["Variables Behavior"] });
	    
	    // Node subprocesses
	    this.graph.addNode("Clean", { x: -110, y: 86, size: this.SUBPSZ, label: "Cleaning", forceLabel: true, type: "gradient", color: this.SUBPCO["Data Quality"]["Clean"] });
	    
	    this.graph.addNode("Nulls", { x: -40, y: 130, size: this.SUBPSZ, label: "Nulls", forceLabel: true, type: "gradient", color: this.SUBPCO["Data Quality"]["Nulls"] });
	    this.graph.addNode("Rolling Mean", { x: 40, y: 112, size: this.ACTVSZ, label: "Rolling Mean", forceLabel: true, path: "clean/rm", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["Rolling Mean"] });
	    this.graph.addNode("Decision Tree", { x: 32, y: 104, size: this.ACTVSZ, label: "Decision Tree", forceLabel: true, path: "clean/dtr", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["Decision Tree"] });
	    this.graph.addNode("Stochastic Gradient", { x: 24, y: 96, size: this.ACTVSZ, label: "Stochastic Gradient", forceLabel: true, path: "clean/sgb", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["Stochastic Gradient"] });
	    this.graph.addNode("Locally Weighted", { x: 16, y: 88, size: this.ACTVSZ, label: "Locally Weighted", forceLabel: true, path: "clean/lwr", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["Locally Weighted"] });
	    this.graph.addNode("Random Forest", { x: 8, y: 80, size: this.ACTVSZ, label: "Random Forest", forceLabel: true, path: "clean/rfr", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["Random Forest"] });
	    this.graph.addNode("Legendre", { x: 0, y: 72, size: this.ACTVSZ, label: "Legendre", forceLabel: true, path: "clean/lgd", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["Legendre"] });
	    this.graph.addNode("KNN", { x: -8, y: 64, size: this.ACTVSZ, label: "KNN", forceLabel: true, path: "clean/knn", type: "gradient", color: this.ACTVCO["Data Quality"]["Nulls"]["KNN"] });
	    
	    this.graph.addNode("Outliers", { x: -80, y: 70, size: this.SUBPSZ, label: "Outliers", forceLabel: true, type: "gradient", color: this.SUBPCO["Data Quality"]["Outliers"] });
	    this.graph.addNode("Interquartile Range", { x: -56, y: 80, size: this.ACTVSZ, label: "Interquartile Range", forceLabel: true, path: "outliers/iqr", type: "gradient", color: this.ACTVCO["Data Quality"]["Outliers"]["Interquartile Range"] });
	    this.graph.addNode("Z-Score", { x: -58, y: 60, size: this.ACTVSZ, label: "Z-Score", forceLabel: true, path: "outliers/sdv", type: "gradient", color: this.ACTVCO["Data Quality"]["Outliers"]["Z-Score"] });
	    
	    this.graph.addNode("Normalize", { x: -90, y: 10, size: this.SUBPSZ, label: "Normalization", forceLabel: true, type: "gradient", color: this.SUBPCO["Data Quality"]["Normalize"] });
	    this.graph.addNode("MinMax", { x: -60, y: 20, size: this.ACTVSZ, label: "MinMax", forceLabel: true, path: "normalize/minmax", type: "gradient", color: this.ACTVCO["Data Quality"]["Normalize"]["MinMax"] });
	    this.graph.addNode("Standard", { x: -64, y: 36, size: this.ACTVSZ, label: "Standard", forceLabel: true, path: "normalize/standard", type: "gradient", color: this.ACTVCO["Data Quality"]["Normalize"]["Standard"] });
	    this.graph.addNode("MaxAbs", { x: -64, y: -16, size: this.ACTVSZ, label: "MaxAbs", forceLabel: true, path: "normalize/maxabs", type: "gradient", color: this.ACTVCO["Data Quality"]["Normalize"]["MaxAbs"] });
	    this.graph.addNode("Robust", { x: -60, y: 0, size: this.ACTVSZ, label: "Robust", forceLabel: true, path: "normalize/robust", type: "gradient", color: this.ACTVCO["Data Quality"]["Normalize"]["Robust"] });
	    
	    this.graph.addNode("Transform", { x: -100, y: -58, size: this.SUBPSZ, label: "Transformation", forceLabel: true, type: "gradient", color: this.SUBPCO["Data Quality"]["Transform"] });
	    this.graph.addNode("Linear", { x: -64, y: -90, size: this.ACTVSZ, label: "Linear", forceLabel: true, path: "transform/linear/" /* + this.factor */, type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Linear"] });
	    this.graph.addNode("Square Root", { x: -60, y: -76, size: this.ACTVSZ, label: "Square Root", forceLabel: true, path: "transform/sqrt/" + this.factor, type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Square Root"] });
	    this.graph.addNode("Quadratic", { x: -58, y: -64, size: this.ACTVSZ, label: "Quadratic", forceLabel: true, path: "transform/quadratic/" + this.factor, type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Quadratic"] });
	    this.graph.addNode("Logarithm", { x: -60, y: -50, size: this.ACTVSZ, label: "Logarithm", forceLabel: true, path: "transform/log/" + this.factor, type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Logarithm"] });
	    this.graph.addNode("Differencing", { x: -64, y: -36, size: this.ACTVSZ, label: "Differencing", forceLabel: true, path: "transform/diff/" + this.factor, type: "gradient", color: this.ACTVCO["Data Quality"]["Transform"]["Differencing"] });
	    
	    this.graph.addNode("DimRed", { x: 20, y: -30, size: this.SUBPSZ, label: "Dim. Reduction", forceLabel: true, type: "gradient", color: this.SUBPCO["Data Reduction"]["DimRed"] });
	    this.graph.addNode("Factor Analysis", { x: 50, y: -40, size: this.ACTVSZ, label: "Factor Analysis", forceLabel: true, path: "reduce/factor/" + this.n_comp, type: "gradient", color: this.ACTVCO["Data Reduction"]["DimRed"]["Factor Analysis"] });
	    this.graph.addNode("PCA and correlation", { x: 40, y: -10, size: this.ACTVSZ, label: "PCA and correlation", forceLabel: true, path: "reduce/manual/" /* + this.n_comp */, type: "gradient", color: this.ACTVCO["Data Reduction"]["DimRed"]["PCA and correlation"] });
	    
	    this.graph.addNode("Analysis", { x: 90, y: 36, size: this.SUBPSZ, label: "Analysis", forceLabel: true, type: "gradient", color: this.SUBPCO["Variables Behavior"]["Analysis"] });
	    this.graph.addNode("Trend", { x: 110, y: 68, size: this.ACTVSZ, label: "Trend", forceLabel: true, path: "", type: "gradient", color: this.ACTVCO["Variables Behavior"]["Analysis"]["Trend"] });
	    this.graph.addNode("Cyclicity", { x: 120, y: 56, size: this.ACTVSZ, label: "Cyclicity", forceLabel: true, path: "/spiral", type: "gradient", color: this.ACTVCO["Variables Behavior"]["Analysis"]["Cyclicity"] });
	    this.graph.addNode("Seasonality", { x: 124, y: 40, size: this.ACTVSZ, label: "Seasonality", forceLabel: true, path: "", type: "gradient", color: this.ACTVCO["Variables Behavior"]["Analysis"]["Seasonality"] });
	    this.graph.addNode("Noise", { x: 120, y: 26, size: this.ACTVSZ, label: "Noise", forceLabel: true, path: "", type: "gradient", color: this.ACTVCO["Variables Behavior"]["Analysis"]["Noise"] });
	    
	    // Edge processes
	    // this.graph.addEdge("Data Quality", "Data Reduction", { type: "curve", curvature: 0.4, label: "macrotarea", size: 7, color: this.GREEN });
	    // this.graph.addEdge("Data Reduction", "Variables Behavior", { type: "curve", curvature: 0.4, label: "macrotarea", size: 7, color: this.GREEN });
	    
	    // Edge subprocesses
	    this.graph.addEdge("Data Quality", "Clean", { type: "curve", curvature: 0.2, /*label: "tarea",*/ size: 5, color: this.SUBPCO["Data Quality"]["Clean"] });
	    
	    this.graph.addEdge("Clean", "Nulls", { type: "curve", curvature: 0.25, /*label: "subtarea",*/ size: 5, color: this.SUBPCO["Data Quality"]["Nulls"] });
	    this.graph.addEdge("Nulls", "Rolling Mean", { type: "curve", curvature: 0.25, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["Rolling Mean"] });
	    this.graph.addEdge("Nulls", "Decision Tree", { type: "curve", curvature: 0.2, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["Decision Tree"] });
	    this.graph.addEdge("Nulls", "Stochastic Gradient", { type: "curve", curvature: 0.2, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["Stochastic Gradient"] });
	    this.graph.addEdge("Nulls", "Locally Weighted", { type: "curve", curvature: 0.2, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["Locally Weighted"] });
	    this.graph.addEdge("Nulls", "Legendre", { type: "curve", curvature: 0.2, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["Legendre"] });
	    this.graph.addEdge("Nulls", "Random Forest", { type: "curve", curvature: 0.2, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["Random Forest"] });
	    this.graph.addEdge("Nulls", "KNN", { type: "curve", curvature: 0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Nulls"]["KNN"] });
	    
	    this.graph.addEdge("Rolling Mean", "Data Reduction", { type: "curve", curvature: 0.5, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("Decision Tree", "Data Reduction", { type: "curve", curvature: 0.4, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("Stochastic Gradient", "Data Reduction", { type: "curve", curvature: 0.3, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("Locally Weighted", "Data Reduction", { type: "curve", curvature: 0.25, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("Legendre", "Data Reduction", { type: "curve", curvature: 0.2, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("Random Forest", "Data Reduction", { type: "curve", curvature: 0.2, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("KNN", "Data Reduction", { type: "curve", curvature: 0.1, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    
	    this.graph.addEdge("Clean", "Outliers", { type: "curve", curvature: -0.2, /*label: "subtarea",*/ size: 5, color: this.SUBPCO["Data Quality"]["Outliers"] });
	    this.graph.addEdge("Outliers", "Interquartile Range", { type: "curve", curvature: 0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Outliers"]["Interquartile Range"] });
	    this.graph.addEdge("Outliers", "Z-Score", { type: "curve", curvature: -0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Outliers"]["Z-Score"] });
	    
	    this.graph.addEdge("Interquartile Range", "Data Reduction", { type: "curve", curvature: 0.4, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("Z-Score", "Data Reduction", { type: "curve", curvature: 0.4, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    
	    this.graph.addEdge("Data Quality", "Normalize", { type: "curve", curvature: 0.2, /*label: "tarea",*/ size: 5, color: this.SUBPCO["Data Quality"]["Normalize"] });
	    this.graph.addEdge("Normalize", "MinMax", { type: "curve", curvature: 0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Normalize"]["MinMax"] });
	    this.graph.addEdge("Normalize", "Standard", { type: "curve", curvature: 0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Normalize"]["Standard"] });
	    this.graph.addEdge("Normalize", "MaxAbs", { type: "curve", curvature: -0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Normalize"]["MaxAbs"] });
	    this.graph.addEdge("Normalize", "Robust", { type: "curve", curvature: -0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Normalize"]["Robust"] });
	    
	    this.graph.addEdge("MinMax", "Data Reduction", { type: "curve", curvature: 0.1, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("Standard", "Data Reduction", { type: "curve", curvature: 0.3, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("MaxAbs", "Data Reduction", { type: "curve", curvature: -0.2, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("Robust", "Data Reduction", { type: "curve", curvature: -0.1, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    
	    this.graph.addEdge("Data Quality", "Transform", { type: "curve", curvature: -0.2, /*label: "tarea",*/ size: 5, color: this.SUBPCO["Data Quality"]["Transform"] });
	    this.graph.addEdge("Transform", "Linear", { type: "curve", curvature: -0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Linear"] });
	    this.graph.addEdge("Transform", "Quadratic", { type: "curve", curvature: -0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Quadratic"] });
	    this.graph.addEdge("Transform", "Square Root", { type: "curve", curvature: -0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Square Root"] });
	    this.graph.addEdge("Transform", "Logarithm", { type: "curve", curvature: 0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Logarithm"] });
	    this.graph.addEdge("Transform", "Differencing", { type: "curve", curvature: 0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Quality"]["Transform"]["Differencing"] });
	    
	    this.graph.addEdge("Linear", "Data Reduction", { type: "curve", curvature: -0.4, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("Quadratic", "Data Reduction", { type: "curve", curvature: -0.4, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("Square Root", "Data Reduction", { type: "curve", curvature: -0.4, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("Logarithm", "Data Reduction", { type: "curve", curvature: -0.4, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("Differencing", "Data Reduction", { type: "curve", curvature: -0.4, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    
	    this.graph.addEdge("Data Reduction", "DimRed", { type: "curve", curvature: -0.2, /*label: "tarea",*/ size: 5, color: this.SUBPCO["Data Reduction"]["DimRed"] });
	    this.graph.addEdge("DimRed", "Factor Analysis", { type: "curve", curvature: -0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Reduction"]["DimRed"]["Factor Analysis"] });
	    this.graph.addEdge("DimRed", "PCA and correlation", { type: "curve", curvature: 0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Data Reduction"]["DimRed"]["PCA and correlation"] });
	    
	    this.graph.addEdge("Factor Analysis", "Variables Behavior", { type: "curve", curvature: -0.4, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    this.graph.addEdge("PCA and correlation", "Variables Behavior", { type: "curve", curvature: 0.2, /*label: "macrotarea",*/ size: 3, color: this.GREEN });
	    
	    this.graph.addEdge("Variables Behavior", "Analysis", { type: "curve", curvature: 0.2, /*label: "tarea",*/ size: 5, color: this.SUBPCO["Variables Behavior"]["Analysis"] });
	    this.graph.addEdge("Analysis", "Trend", { type: "curve", curvature: 0.2, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Variables Behavior"]["Analysis"]["Trend"] });
	    this.graph.addEdge("Analysis", "Cyclicity", { type: "curve", curvature: 0.1, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Variables Behavior"]["Analysis"]["Cyclicity"] });
	    this.graph.addEdge("Analysis", "Seasonality", { type: "curve", curvature: -0.2, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Variables Behavior"]["Analysis"]["Seasonality"] });
	    this.graph.addEdge("Analysis", "Noise", { type: "curve", curvature: -0.2, /*label: "microtarea",*/ size: 3, color: this.ACTVCO["Variables Behavior"]["Analysis"]["Noise"] });
	    
	    // Graph borders
	    this.graph.addNode("Start", { x: -150, y: 66, size: 24, label: "Start", forceLabel: true, type: "gradient", color: this.LIGHTBLUE });
	    this.graph.addNode("End", { x: 150, y: 56, size: 24, label: "End", forceLabel: true, type: "gradient", color: this.LIGHTBLUE });
	    this.graph.addEdge("Start", "Data Quality", { type: "curve", curvature: -0.1, /*label: "start",*/ size: 2, color: this.LIGHTBLUE });
	    this.graph.addEdge("Trend", "End", { type: "curve", curvature: 0.4, /*label: "end",*/ size: 2, color: this.LIGHTBLUE });
	    this.graph.addEdge("Cyclicity", "End", { type: "curve", curvature: 0.1, /*label: "end",*/ size: 2, color: this.LIGHTBLUE });
	    this.graph.addEdge("Seasonality", "End", { type: "curve", curvature: -0.2, /*label: "end",*/ size: 2, color: this.LIGHTBLUE });
	    this.graph.addEdge("Noise", "End", { type: "curve", curvature: -0.2, /*label: "end",*/ size: 2, color: this.LIGHTBLUE });
	    
	    // Edge sequences
	    // this.graph.addEdge("Clean", "Normalize", { type: "curve", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    // this.graph.addEdge("Normalize", "Transform", { type: "curve", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    // this.graph.addEdge("Transform", "DimRed", { type: "curve", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    // this.graph.addEdge("DimRed", "Trend", { type: "curve", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    // this.graph.addEdge("Trend", "Cyclicity", { type: "curve", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    // this.graph.addEdge("Cyclicity", "Seasonality", { type: "curve", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    // this.graph.addEdge("Seasonality", "Clean", { type: "curve", label: "sequence", size: 3, color: this.LIGHTBLUE });
	    
	    //* this.graph.nodes().forEach((node, i) => {
	    //*     const angle = (i * 2 * Math.PI) / this.graph.order;
	    //*     this.graph.setNodeAttribute(node, "x", 100 * Math.cos(angle));
	    //*     this.graph.setNodeAttribute(node, "y", 100 * Math.sin(angle));
	    //* });
	    
	    var last_madepath = "";
	    for (var madepath in itpath) {
		if (this.graph.getNodeAttribute(itpath[madepath], 'color') == this.GREEN || this.graph.getNodeAttribute(itpath[madepath], 'color') == this.LIGHTBLUE) {
		    this.graph.setNodeAttribute(itpath[madepath], 'color', this.LIGHTBLUE);
		    if (this.graph.areNeighbors(itpath[madepath], "Data Quality") && (this.graph.getNodeAttribute("Data Quality", 'color') == this.GREEN || this.graph.getNodeAttribute("Data Quality", 'color') == this.ORANGE)) {
			this.graph.setNodeAttribute("Data Quality", 'color', this.LIGHTBLUE);
		    }
		    if (this.graph.areNeighbors(itpath[madepath], "Data Reduction") && (this.graph.getNodeAttribute("Data Reduction", 'color') == this.GREEN || this.graph.getNodeAttribute("Data Reduction", 'color') == this.ORANGE)) {
			this.graph.setNodeAttribute("Data Reduction", 'color', this.LIGHTBLUE);
		    }
		    if (this.graph.areNeighbors(itpath[madepath], "Variables Behavior") && (this.graph.getNodeAttribute("Variables Behavior", 'color') == this.GREEN || this.graph.getNodeAttribute("Variables Behavior", 'color') == this.ORANGE)) {
			this.graph.setNodeAttribute("Variables Behavior", 'color', this.LIGHTBLUE);
		    }
		    if (last_madepath !== "") {
			if (this.graph.hasEdge(last_madepath, itpath[madepath])) {
			    this.graph.setEdgeAttribute(last_madepath, itpath[madepath], 'color', this.LIGHTBLUE);
			}
		    }
		    if (this.graph.getNodeAttribute("Data Quality", 'color') == this.LIGHTBLUE) {
			if (this.graph.hasEdge(itpath[madepath], "Data Quality")) {
			    this.graph.setEdgeAttribute(itpath[madepath], "Data Quality", 'color', this.LIGHTBLUE);
			}
			if (this.graph.hasEdge("Data Quality", itpath[madepath])) {
			    this.graph.setEdgeAttribute("Data Quality", itpath[madepath], 'color', this.LIGHTBLUE);
			}
		    }
		    if (this.graph.getNodeAttribute("Data Reduction", 'color') == this.LIGHTBLUE) {
			if (this.graph.hasEdge(itpath[madepath], "Data Reduction")) {
			    this.graph.setEdgeAttribute(itpath[madepath], "Data Reduction", 'color', this.LIGHTBLUE);
			}
			if (this.graph.hasEdge("Data Reduction", itpath[madepath])) {
			    this.graph.setEdgeAttribute("Data Reduction", itpath[madepath], 'color', this.LIGHTBLUE);
			}
		    }
		    if (this.graph.getNodeAttribute("Variables Behavior", 'color') == this.LIGHTBLUE) {
			if (this.graph.hasEdge(itpath[madepath], "Variables Behavior")) {
			    this.graph.setEdgeAttribute(itpath[madepath], "Variables Behavior", 'color', this.LIGHTBLUE);
			}
			if (this.graph.hasEdge("Variables Behavior", itpath[madepath])) {
			    this.graph.setEdgeAttribute("Variables Behavior", itpath[madepath], 'color', this.LIGHTBLUE);
			}
		    }
		    last_madepath = itpath[madepath];
		}
	    }
	    
	    this.renderer = new Sigma(this.graph, this.container, {
		nodeProgramClasses: {
		    // image: createNodeImageProgram(),
		    gradient: NodeGradientProgram,
		},
		minCameraRatio: 1,
		maxCameraRatio: 10,
		// allowInvalidContainer: true,
		renderEdgeLabels: true,
		// defaultEdgeType: "curve",
		edgeProgramClasses: {
		    curve: EdgeCurveProgram,
		}
	    });
	    
	    // Create the spring layout and start it
	    //* this.layout = new ForceLayout(this.graph, { maxIterations: 50 });
	    this.loading_data = false
	    //* this.layout.start();
	    
	    //* setTimeout(() => {this.layout.stop();}, 4000);
	    
	    this.renderer.on("clickNode", ({ node }) => this.execActivity("clickNode", "node", node));
	    this.renderer.on("enterNode", ({ node }) => this.showGuide("enterNode", "node", node));
	    this.renderer.on("leaveNode", ({ node }) => this.hideGuide("leaveNode", "node", node));
	    
	    onStoryDown(() => {
		//* this.layout.kill();
		this.renderer.kill();
	    });
	},
	async showGuide(event, itemType, item) {
	    this.currentGuide = -1;
	    if (event === "enterNode") {
		let label;
		if (item && itemType) {
		    if (itemType === "node") {
			label = this.graph.getNodeAttribute(item, "label");
			switch(label) {
			case "Data Quality": this.currentGuide = 0; break;
			case "Cleaning": this.currentGuide = 1; break;
			case "Nulls": this.currentGuide = 2; break;
			case "Rolling Mean": this.currentGuide = 3; break;
			case "Decision Tree": this.currentGuide = 4; break;
			case "Stochastic Gradient": this.currentGuide = 5; break;
			case "Locally Weighted": this.currentGuide = 6; break;
			case "Random Forest": this.currentGuide = 7; break;
			case "Legendre": this.currentGuide = 8; break;
			case "KNN": this.currentGuide = 9; break;
			case "Outliers": this.currentGuide = 10; break;
			case "Interquartile Range": this.currentGuide = 11; break;
			case "Z-Score": this.currentGuide = 12; break;
			case "Normalization": this.currentGuide = 13; break;
			case "Standard": this.currentGuide = 14; break;
			case "MinMax": this.currentGuide = 15; break;
			case "Robust": this.currentGuide = 16; break;
			case "MaxAbs": this.currentGuide = 17; break;
			case "Transformation": this.currentGuide = 18; break;
			case "Differencing": this.currentGuide = 19; break;
			case "Logarithm": this.currentGuide = 20; break;
			case "Quadratic": this.currentGuide = 21; break;
			case "Square Root": this.currentGuide = 22; break;
			case "Linear": this.currentGuide = 23; break;
			case "Data Reduction": this.currentGuide = 24; break;
			case "Dim. Reduction": this.currentGuide = 25; break;
			case "PCA and correlation": this.currentGuide = 26; break;
			case "Factor Analysis": this.currentGuide = 27; break;
			case "Variables Behavior": this.currentGuide = 28; break;
			case "Analysis": this.currentGuide = 29; break;
			case "Trend": this.currentGuide = 30; break;
			case "Seasonality": this.currentGuide = 31; break;
			case "Cyclicity": this.currentGuide = 32; break;
			case "Noise": this.currentGuide = 33; break;
			default: this.currentGuide = -1;
			}
		    }
		}
	    }
	    if (this.currentGuide >= 0) {
		// this.$refs.guide.open(this.$refs[this.guide[this.currentGuide].ref]);
		this.tooltipText = this.guide[this.currentGuide].text;
		this.tooltipVisible = true;
	    }
	    console.log("[", event, "]:", itemType, this.graph.getNodeAttribute(item, "label"), this.currentGuide);
	},
	async hideGuide(event, itemType, item) {
	    if (this.currentGuide >= 0) {
		// this.$refs.guide.close();
		this.tooltipVisible = false;
		this.tooltipText = '';
	    }
	    console.log("[", event, "]:", itemType, this.graph.getNodeAttribute(item, "label"), this.currentGuide);
	}
    },
    computed: {
	// end_year: function() {
	//     let res = this.start_year + (this.rangeYear * this.params.points_per_period) / 12
	//     return this.start_year ? Math.round(res) : null
	// }
    },
    mounted: function() {
	this.dataset = this.$route.params.dataset;
	this.station = this.$route.params.station;
	document.getElementById("dynNet").href=`/net/${this.dataset}/${this.station}`;
	document.getElementById("dynVisualize").href=`/visualize/${this.dataset}/${this.station}`;
	document.getElementById("dynStats").href=`/stats/${this.dataset}/${this.station}`;
	document.getElementById("dynSpiral").href=`/spiral/${this.dataset}/${this.station}`;
	console.log("[ Mounted Network View ]: (", this.dataset, ",", this.station, ")");
	axios.get(
	    "http://localhost:8080/data/" + this.dataset + "/" + this.station,
	    { crossdomain: true }
	).then(async meta => {
	    console.log("[ Mounted Raw Data Length ]:", meta.data.length)
	});
	this.showNetwork();
    },
    watch: {
	// end_year(newValue) {
	//     console.log("[ WATCH END_YEAR ]", newValue);
	//     this.raw_data = this.orig_data.filter(x => { return x.date > `${this.start_year}-01-01` });
	//     this.renderSpiral();
	//     this.spiral.redraw();
	// }
    }
}
</script>

<style>
img {
    width: 100%;
    height: auto;
}
.labels.segment {
    font: sans-serif;
    font-size: 13px;
    font-family: Arvo;
    font-weight: 300;
}
.custom-step {
    width: 4px;
    height: 4px;
    border-radius: 50%;
    position: relative;
    box-shadow: 0 0 0 3px #ccc;
    background-color: #fff;
    z-index: 3;
}
.custom-step.active {
    box-shadow: 0 0 0 3px #3498db;
    background-color: #3498db;
}
.custom-step-bar.active {
    z-index: 1;
    position: relative;
    margin-top: -25px;
    width: 100%;
    height: 25px;
    border-radius: 25px;
    background-color: rgb(85, 85, 85);
}
table.blockTable {
    writing-mode: horizontal-lr;
    min-width: 50px;
    /* for firefox */
}
.firstRow {
    width: 38vw;
}
td.slideOp:hover {
    background-color: rgba(6, 10, 223, 0.109);
    cursor: pointer;
}
.dataframe tbody tr th:only-of-type {
    vertical-align: middle;
}

.dataframe tbody tr th {
    vertical-align: top;
}

.dataframe thead th {
    text-align: right;
}
div.load-layer {
    background-color: #efefef;
    position: absolute;
    width: 100%;
    height: 100%;
    z-index: 1000;
    top: 0px;
    left: 0px;
    opacity: 0.8;
    /* in FireFox */
    filter: alpha(opacity=80);
    /* in IE */
}
.loader {
    top: 20%;
}
.tooltip {
  position: absolute;
  bottom: 0%;
  left: 80%;
  /* position: fixed; */
  /* bottom: 10px; */
  /* right: 10px; */
  transform: translateX(-50%);
  padding: 10px;
  background-color: #333;
  color: white;
  border-radius: 5px;
  white-space: nowrap;
  visibility: visible;
  opacity: 0.9;
  transition: opacity 0.2s;
}
.legend-tooltip {
  position: absolute;
  top: 0%;
  right: 0%;
  background-color: #fff;
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 5px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}
.legend-item {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
}
.legend-item:last-child {
  margin-bottom: 0;
}
.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 10px;
}
.redlg { background-color: red; }
.bluelg { background-color: lightblue; }
.graylg { background-color: lightgray; }
.greenlg { background-color: lightgreen; }
.orangelg { background-color: orange; }
</style>
