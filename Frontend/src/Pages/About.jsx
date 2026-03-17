// export default function About() {
//   return (
//     <div className="p-6 overflow-y-scroll h-screen bg-[#f4f7fb]">

//       {/* Navbar */}
//       <div className="bg-blue-600 text-white p-4 text-center sticky top-0">
//         <a href="#overview" className="mx-3 font-bold">Overview</a>
//         <a href="#login" className="mx-3 font-bold">Login</a>
//         <a href="#dashboard" className="mx-3 font-bold">Dashboard</a>
//         <a href="#features" className="mx-3 font-bold">Features</a>
//         <a href="#workflow" className="mx-3 font-bold">Workflow</a>
//         <a href="#technical" className="mx-3 font-bold">Technical</a>
//       </div>

//       {/* Content */}
//       <div className="mt-6 space-y-6">

//         <div id="overview" className="bg-white p-6 rounded-xl shadow">
//           <h1 className="text-blue-900 text-2xl font-bold">AI Diagnostics System</h1>
//           <p>This system helps doctors analyze X-rays, MRI, ECG quickly using AI.</p>
//         </div>

//         <div id="login" className="bg-white p-6 rounded-xl shadow">
//           <h2 className="text-blue-900 text-xl font-bold">Login System</h2>
//           <ul className="list-disc ml-6">
//             <li>Email & Password input</li>
//             <li>Authentication check</li>
//             <li>Redirect to dashboard</li>
//           </ul>
//         </div>

//         <div id="dashboard" className="bg-white p-6 rounded-xl shadow">
//           <h2 className="text-blue-900 text-xl font-bold">Dashboard</h2>
//           <ul className="list-disc ml-6">
//             <li>Sidebar navigation</li>
//             <li>Stats cards</li>
//             <li>Patient table</li>
//           </ul>
//         </div>

//         <div id="features" className="bg-white p-6 rounded-xl shadow">
//           <h2 className="text-blue-900 text-xl font-bold">Features</h2>
//           <ul className="list-disc ml-6">
//             <li>Scan Upload</li>
//             <li>AI Diagnosis</li>
//             <li>History Tracking</li>
//           </ul>
//         </div>

//         <div id="workflow" className="bg-white p-6 rounded-xl shadow">
//           <h2 className="text-blue-900 text-xl font-bold">Workflow</h2>
//           <ul className="list-disc ml-6">
//             <li>Login → Upload → AI → Result</li>
//           </ul>
//         </div>

//         <div id="technical" className="bg-white p-6 rounded-xl shadow">
//           <h2 className="text-blue-900 text-xl font-bold">Technical</h2>
//           <ul className="list-disc ml-6">
//             <li>React + Tailwind</li>
//             <li>Routing system</li>
//             <li>LocalStorage auth</li>
//           </ul>
//         </div>

//       </div>

//     </div>
//   )
// }
import React from "react";

export default function About() {
  return (
    <div style={{ fontFamily: "Arial", margin: 0, background: "#f4f7fb", scrollBehavior: "smooth" }}>

      {/* NAVBAR */}
      <div style={{
        background: "#2563eb",
        padding: "15px",
        textAlign: "center",
        position: "sticky",
        top: 0
      }}>
        <a href="#overview" style={navLink}>Overview</a>
        <a href="#login" style={navLink}>Login System</a>
        <a href="#dashboard" style={navLink}>Dashboard</a>
        <a href="#features" style={navLink}>Features</a>
        <a href="#workflow" style={navLink}>Workflow</a>
        <a href="#technical" style={navLink}>Technical Logic</a>
      </div>

      <div style={{ padding: "30px" }}>

        {/* OVERVIEW */}
        <div id="overview" style={card}>
          <h1>AI Diagnostics System</h1>

          <p>
            This system is designed to help doctors quickly analyze medical data like X-rays, MRI, and ECG.
            It reduces diagnosis time and improves healthcare efficiency.
          </p>

          <h2>Problem</h2>
          <p>
            In many areas, especially rural regions, there are very few radiologists.
            Patients have to wait for hours or days to get results.
          </p>

          <h2>Solution</h2>
          <p>
            Our system uses Artificial Intelligence to analyze reports instantly and display results on a dashboard.
          </p>
        </div>

        {/* LOGIN */}
        <div id="login" style={card}>
          <h2>Login System (Authentication)</h2>

          <h3>UI Explanation</h3>
          <ul>
            <li>Left side → Medical illustration</li>
            <li>Right side → Login form</li>
            <li>Fields → Email & Password</li>
            <li>Button → Login</li>
            <li>Link → Register page</li>
          </ul>

          <h3>Working Logic</h3>
          <ul>
            <li>User enters email and password</li>
            <li>System checks credentials</li>
            <li>If correct → Dashboard open</li>
            <li>If wrong → Error message</li>
          </ul>

          <h3>Token System</h3>
          <p>
            After login, a token is stored in localStorage.
            This token keeps user logged in even after refresh.
          </p>

          <h3>Navigation</h3>
          <ul>
            <li>Register link → goes to Register page</li>
            <li>Login success → redirect to dashboard</li>
          </ul>
        </div>

        {/* DASHBOARD */}
        <div id="dashboard" style={card}>
          <h2>Dashboard (Main System UI)</h2>

          <h3>Layout Structure</h3>
          <ul>
            <li>Left Sidebar → Navigation menu</li>
            <li>Top Bar → Dashboard title + Logout button</li>
            <li>Main Area → Data and stats</li>
          </ul>

          <h3>Sidebar Features</h3>
          <ul>
            <li>Dashboard</li>
            <li>X-ray Analysis</li>
            <li>MRI Analysis</li>
            <li>ECG Analysis</li>
            <li>History</li>
            <li>Trends</li>
            <li>About</li>
          </ul>

          <h3>Stats Cards</h3>
          <ul>
            <li>Total Patients</li>
            <li>Total Scans</li>
            <li>Total Reports</li>
          </ul>

          <h3>Patient Table</h3>
          <ul>
            <li>Name of patient</li>
            <li>Scan type (X-ray / MRI / ECG)</li>
            <li>Result (Normal / Disease)</li>
            <li>Date</li>
          </ul>

          <h3>Purpose</h3>
          <p>
            Helps doctors quickly view patient history and results.
          </p>
        </div>

        {/* FEATURES */}
        <div id="features" style={card}>
          <h2>Core Features</h2>

          <h3>1. Scan Upload</h3>
          <p>Doctors can upload medical scans like X-ray, MRI, or ECG.</p>

          <h3>2. AI Diagnosis</h3>
          <p>The system analyzes the scan using AI models and detects diseases.</p>

          <h3>3. Instant Result</h3>
          <p>Results are generated quickly and shown on dashboard.</p>

          <h3>4. History Tracking</h3>
          <p>All past reports are stored and can be viewed anytime.</p>

          <h3>5. Secure System</h3>
          <p>Login system ensures only authorized users can access data.</p>
        </div>

        {/* WORKFLOW */}
        <div id="workflow" style={card}>
          <h2>System Workflow</h2>

          <ul>
            <li>Step 1 → User logs in</li>
            <li>Step 2 → Upload scan</li>
            <li>Step 3 → AI processes data</li>
            <li>Step 4 → Result generated</li>
            <li>Step 5 → Data saved in dashboard</li>
          </ul>

          <h3>Logout Process</h3>
          <ul>
            <li>User clicks logout</li>
            <li>Token removed from localStorage</li>
            <li>User redirected to login page</li>
          </ul>
        </div>

        {/* TECHNICAL */}
        <div id="technical" style={card}>
          <h2>Technical Logic</h2>

          <h3>Frontend</h3>
          <ul>
            <li>React + Tailwind CSS</li>
          </ul>

          <h3>Routing</h3>
          <ul>
            <li>/ → Login</li>
            <li>/register → Register</li>
            <li>/dashboard → Dashboard</li>
          </ul>

          <h3>State Management</h3>
          <p>useState is used to store user input.</p>

          <h3>Navigation</h3>
          <p>useNavigate is used for routing.</p>

          <h3>Authentication</h3>
          <p>Token stored in localStorage.</p>
        </div>

      </div>
    </div>
  );
}

// styles
const navLink = {
  color: "white",
  margin: "0 15px",
  textDecoration: "none",
  fontWeight: "bold"
};

const card = {
  background: "white",
  padding: "25px",
  marginBottom: "25px",
  borderRadius: "12px",
  boxShadow: "0 6px 12px rgba(0,0,0,0.1)"
};