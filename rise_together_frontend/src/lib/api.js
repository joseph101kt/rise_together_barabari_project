import axios from "axios";

//backend base URL 
const API=axios.create({
    baseURL:import.meta.env.VITE_BASEURL,
});

API.interceptors.request.use(
    (config)=>{
        const token=localStorage.getItem("token");
        if(token){
            config.headers.Authorization=`Bearer ${token}`;
        }
        return config;
    },
    (error)=>{
        return Promise.reject(error);
    }
);
export default API;