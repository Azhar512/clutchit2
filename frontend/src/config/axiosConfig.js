import axios from 'axios';

// Use environment variables for flexibility between environments
const API_URL = process.env.REACT_APP_API_URL || 'http://82.25.110.175:5000';

axios.defaults.baseURL = API_URL;

export default axios;