<template>
  <v-container class="my-6" fluid>
    <!-- <v-row justify="center" dense v-if="datasetSelected"> -->
    <!--   <v-col class="text-center text-h4 text-capitalize">Dataset: {{ dataset }} -->
    <!--   </v-col> -->
    <!-- </v-row> -->
    <!-- <v-row -->
    <!--   class="text-center" -->
    <!--   justify="center" -->
    <!--   align="center" -->
    <!--   v-if="!datasetSelected"> -->
    <!--   <v-col cols="3"> -->
    <!--     <h1>Dataset:</h1> -->
    <!--   </v-col> -->
    <!--   <v-col cols="3"> -->
    <!--     <v-select -->
    <!--       v-model="dataset" -->
    <!--       :items="items" -->
    <!--       item-text="text" -->
    <!--       item-value="value" -->
    <!--       label="Select" -->
    <!--       persistent-hint -->
    <!--       single-line> -->
    <!-- 	</v-select> -->
    <!--   </v-col> -->
    <!--   <v-col cols="2"> -->
    <!--     <v-btn color="primary" @click="datasetSelected = true">Use</v-btn> -->
    <!--   </v-col> -->
    <!-- </v-row> -->
    <!-- <v-row class="text-center" v-if="datasetSelected"> -->
    <!--   <v-col> -->
    <!--     <time-series v-bind:dataset="dataset" v-bind:station="station" /> -->
    <!--   </v-col> -->
    <!-- </v-row> -->
  </v-container>
</template>

<script>
// import TimeSeries from "../components/TimeSeries.vue"
// @ is an alias to /src

export default {
    name: "Home",
    // components: { TimeSeries },
    data: () => ({
	// dataset: "majes",
	// station: "majes",
	// items: [
	//     { text: "Madrid", value: "madrid" },
	//     { text: "Peru", value: "aqp" },
	//     { text: "India", value: "india" },
	//     { text: "Brasil", value: "brasil" }
	// ],
	// datasetSelected: false
    }),
    methods: {
    }
};
</script>
