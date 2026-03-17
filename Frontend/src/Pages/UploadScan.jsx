import { useState } from "react"
import { useNavigate } from "react-router-dom"

import Sidebar from "../components/Sidebar"
import Navbar from "../components/Navbar"
import { analyzeScan } from "../Services"

function UploadScan(){

const [file,setFile] = useState(null)
const [preview,setPreview] = useState(null)
const [loading,setLoading] = useState(false)

const navigate = useNavigate()

// 📤 File handle
const handleFile = (e)=>{
const selected = e.target.files[0]
setFile(selected)
setPreview(URL.createObjectURL(selected))
}

// 🚀 Upload + API
const handleUpload = async ()=>{

if(!file){
alert("Upload file first")
return
}

setLoading(true)

const formData = new FormData()
formData.append("file", file)

try{

const data = await analyzeScan(formData)

navigate("/result", { state: data })

}catch{
alert("Error analyzing scan")
}

setLoading(false)
}

return(

<div className="flex bg-blue-50 min-h-screen">

<Sidebar/>

<div className="flex-1">

<Navbar/>

<div className="p-10 flex justify-center">

<div className="bg-white p-10 rounded-2xl shadow-lg w-[400px] text-center">

<h1 className="text-2xl font-bold mb-6 text-blue-700">
Upload Medical Scan
</h1>

{/* Upload Box */}
<label className="border-2 border-dashed border-blue-400 p-6 rounded-xl cursor-pointer block">

<input
type="file"
className="hidden"
onChange={handleFile}
/>

<p className="text-blue-600 font-semibold">
Click to Upload or Drag & Drop
</p>

</label>

{/* Preview */}
{preview && (
<img
src={preview}
className="mt-4 rounded-lg w-64 mx-auto"
/>
)}

{/* Button / Loader */}
{loading ? (

<div className="mt-6">

<div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto"></div>

<p className="mt-2 text-blue-600">
Analyzing Scan...
</p>

</div>

) : (

<button
onClick={handleUpload}
className="mt-6 w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
>
Analyze Scan
</button>

)}

</div>

</div>

</div>

</div>

)

}

export default UploadScan