import Sidebar from "../components/Sidebar"
import Navbar from "../components/Navbar"
import ChartCard from "../components/ChartCard"

function Analytics(){

return(

<div className="flex bg-blue-50 min-h-screen">

<Sidebar/>

<div className="flex-1">

<Navbar/>

<div className="p-8">

<ChartCard/>

</div>

</div>

</div>

)

}

export default Analytics