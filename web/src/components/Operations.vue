<template>
  <v-row align="center" justify="center">
    <v-col>
      <v-select
        v-model="main_operation"
        :items="[
          { text: 'Normalize', value: 'normalize' },
          { text: 'Reduce', value: 'reduce' },
          { text: 'Transform', value: 'transform' }
        ]"
      />
    </v-col>
    <v-col>
      <v-text-field
        label="N° of components (< 3)"
        v-model="n_comp"
        ref="n_comp"
        v-if="main_operation === 'reduce'"
        :rules="[v => (!!v && v < 3) || 'Has to be less than 3']"
      />
      <v-text-field
        label="Transform factor"
        v-model="factor"
        ref="factor"
        v-if="main_operation === 'transform'"
        :rules="[v => !!v || 'Required']"
      />
    </v-col>
    <v-col>
      <v-btn @click="selectedMethod" large color="primary"> Apply</v-btn>
    </v-col>
  </v-row>
</template>

<script>
export default {
  prop: ['value'],
  data: () => ({
    main_operation: 'normalize',
    n_comp: '',
    factor: ''
  }),
  methods: {
    selectedMethod() {
      if (
        this.main_operation === 'reduce' &&
        (this.n_comp === '' || this.n_comp > 3)
      ) {
        this.$refs['n_comp'].validate(true)
        return
      }
      if (this.main_operation === 'transform' && this.factor === '') {
        this.$refs['factor'].validate(true)
        return
      }

      this.$emit('input', {
        operation_name: this.main_operation,
        n_comp: this.n_comp,
        factor: this.factor
      })
      this.n_comp = ''
      this.factor = ''
      this.main_operation = 'scale'
    }
  }
}
</script>
