import { BrowserRouter, Routes, Route } from "react-router-dom"

import Login from "./Pages/Login"
import Dashboard from "./Pages/Dashboard"
import UploadScan from "./Pages/UploadScan"
import Patients from "./Pages/Patients"
import Analytics from "./Pages/Analytics"
import Result from "./Pages/Result"

function App(){

return(

<BrowserRouter>

<Routes>

<Route path="/" element={<Login />} />

<Route path="/dashboard" element={<Dashboard />} />

<Route path="/upload" element={<UploadScan />} />

<Route path="/patients" element={<Patients />} />

<Route path="/analytics" element={<Analytics />} />

<Route path="/result" element={<Result />} />

</Routes>

</BrowserRouter>

)

}

export default App