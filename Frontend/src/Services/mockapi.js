export const analyzeScanMock = async () => {

return new Promise((resolve)=>{
setTimeout(()=>{

resolve({
  disease: "Pneumonia",
  confidence: "94%",
  image: "https://upload.wikimedia.org/wikipedia/commons/8/8e/Chest_Xray_PA_3-8-2010.png"
})

},2000)
})

}