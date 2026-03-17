import { useState } from "react"

function UploadBox({ setFile }) {

const [preview, setPreview] = useState(null)

const handleFile = (file) => {
  setFile(file)
  setPreview(URL.createObjectURL(file))
}

return (

<div className="border-2 border-dashed border-blue-400 p-8 text-center rounded-xl cursor-pointer">

<input
type="file"
className="hidden"
id="fileUpload"
onChange={(e)=>handleFile(e.target.files[0])}
/>

<label htmlFor="fileUpload" className="cursor-pointer">

<p className="text-blue-600 font-semibold">
Click or Drag & Drop Scan
</p>

</label>

{preview && (
<img src={preview} className="mt-4 rounded-lg w-64 mx-auto"/>
)}

</div>

)

}

export default UploadBox