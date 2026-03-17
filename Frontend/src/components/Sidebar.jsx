import { Link } from "react-router-dom"

function Sidebar(){

return(

<div className="w-64 h-screen bg-blue-800 text-white p-6">

<h1 className="text-2xl font-bold mb-10">
AI Diagnostics
</h1>

<ul className="space-y-4">

<li>
<Link to="/dashboard">Dashboard</Link>
</li>

<li>
<Link to="/upload">Upload Scan</Link>
</li>

<li>
<Link to="/result">AI Result</Link>
</li>

</ul>

</div>

)

}

export default Sidebar