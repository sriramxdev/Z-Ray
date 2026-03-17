import axios from "axios"

const API = axios.create({
  baseURL: "http://localhost:5000/api"
})

export const analyzeScanAPI = async (formData) => {

const res = await API.post("/analyze", formData)

return res.data

}