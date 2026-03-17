import Sidebar from "../components/Sidebar"
import Navbar from "../components/Navbar"
import PatientTable from "../components/PatientTable"

function Patients(){

return(

<div className="flex bg-blue-50 min-h-screen">

<Sidebar/>

<div className="flex-1">

<Navbar/>

<div className="p-8">

<h1 className="text-2xl font-bold mb-6">
Patient Records
</h1>

<PatientTable/>

</div>

</div>

</div>

)

}

export default Patients