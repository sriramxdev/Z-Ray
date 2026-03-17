import axios from "axios"

const API = axios.create({
  baseURL: "/diagnose"
})

export const analyzeScanAPI = async (formData, modality = "xray") => {

const res = await API.post(`/${modality}`, formData)

return res.data

}