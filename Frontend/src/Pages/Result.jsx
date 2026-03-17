import Sidebar from "../components/Sidebar"
import Navbar from "../components/Navbar"

function Result(){

return(

<div className="flex bg-blue-50 min-h-screen">

<Sidebar/>

<div className="flex-1">

<Navbar/>

<div className="p-10">

<div className="bg-white p-8 rounded-xl shadow w-[500px]">

<h1 className="text-xl font-bold text-red-500 mb-2">
Pneumonia Detected
</h1>

<p className="mb-4">
Confidence: <span className="font-bold">94%</span>
</p>

<img
src="https://upload.wikimedia.org/wikipedia/commons/8/8e/Chest_Xray_PA_3-8-2010.png"
className="rounded"
/>

</div>

</div>

</div>

</div>

)

}

export default Result