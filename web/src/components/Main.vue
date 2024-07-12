<template>
  <v-container class="my-6">
    <v-row class="text-center">
      <v-col>
        <h1>Videos</h1>
      </v-col>
    </v-row>
    <v-row class="text-center"> </v-row>
  </v-container>
</template>

<script>
import axios from 'axios'

export default {
  name: 'Home',
  components: {},
  data: () => ({
    videos: [
      {
        title: 'Hola'
      },
      {
        title: 'Hola2'
      }
    ],
    show: false,
    formData: {
      user: '',
      passw: ''
    },
    formProps: {
      valid: true,
      userRules: [
        v => !!v || 'Ingrese su usuario de la UNSA',
        v => (v && v.length == 8) || 'El usuario debe tener 8 caracteres'
      ],

      passRules: [
        v => !!v || 'Ingrese su clave',
        v => (v && v.length == 8) || 'La clave debe tener 8 caracteres'
      ]
    },
    loading: false
  }),

  created: function() {
    //https://janotubeback.herokuapp.com/upload
    //http://localhost:1234/upload
    axios({
      method: 'post',
      url: 'http://localhost:1234/getall'
      // headers: {
      //   'Content-Type': 'multipart/form-data'
      // }
    })
      .then(response => {
        //handle success
        console.log(response)
        this.videos = response.data
      })
      .catch(function(response) {
        //handle error
        console.log(response)
      })
  },
  mounted: function() {},

  methods: {
    submit: function() {
      if (this.$refs.form.validate()) {
        // Native form submission is not yet supported
        console.log('submiting', this.formData)
        this.loading = true
        axios
          .get('https://cuantomefalta.app/query', {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
            },
            params: this.formData
          })
          .then(res => {
            if (res.data.error_type) {
              this.$showMessage(
                'El usuario o contraseña son incorrectos',
                'error'
              )
              this.loading = false
              return
            }
            this.$store.commit('setCredentials', this.formData)

            this.loading = false
            this.$router.push({
              name: 'Notas',
              params: { user_data: res.data }
            })
          })
          .catch((err, a) => {
            console.log('Error Login:', err, a, this)
            this.handleError(err)
            this.loading = false
          })
      }
    }
  }
}
</script>
