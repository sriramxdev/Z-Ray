import { USE_BACKEND } from "../config/config"
import { analyzeScanAPI } from "./api"
import { analyzeScanMock } from "./mockapi"

export const analyzeScan = async (formData) => {

if(USE_BACKEND){
  return await analyzeScanAPI(formData)
}else{
  return await analyzeScanMock()
}

}