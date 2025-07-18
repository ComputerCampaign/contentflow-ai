import { createStore } from 'vuex'
import auth from './modules/auth'
import crawler from './modules/crawler'
import xpath from './modules/xpath'
import user from './modules/user'

export default createStore({
  modules: {
    auth,
    crawler,
    xpath,
    user
  }
})