import React, {useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {LayoutDashboard, GraduationCap, ScanLine, Users, BookOpen, Download, ShieldCheck, Clock3, RefreshCw, QrCode, CircleCheck, AlertCircle} from 'lucide-react';
import './style.css';

const API = 'http://127.0.0.1:8000';
function App(){
 const [mode,setMode]=useState('teacher'), [students,setStudents]=useState([]), [lectures,setLectures]=useState([]), [rows,setRows]=useState([]), [selected,setSelected]=useState('1'), [token,setToken]=useState(''), [studentId,setStudentId]=useState('1'), [message,setMessage]=useState(''), [api,setApi]=useState(API), [subject,setSubject]=useState(''), [room,setRoom]=useState('');
 async function call(path,opts={}){const r=await fetch(api+path,opts); const d=await r.json().catch(()=>({detail:'Request failed'})); if(!r.ok)throw Error(d.detail||'Request failed'); return d;}
 async function refresh(){try{const [s,l,a]=await Promise.all([call('/students'),call('/lectures'),call('/attendance')]);setStudents(s);setLectures(l);setRows(a);if(!selected&&l[0])setSelected(String(l[0].id));}catch(e){setMessage(e.message+' — Start backend and seed demo data.');}}
 useEffect(()=>{refresh()},[]);

 async function start(){
 if(!subject.trim() || !room.trim()){
   setMessage('Please enter both subject and classroom.');
   return;
 }
 try{
   let l=await call('/lectures?subject='+encodeURIComponent(subject)+'&classroom='+encodeURIComponent(room),{method:'POST'});
   setSelected(String(l.id));
   setToken('');
   setMessage('Lecture created.');
   await refresh();
 }catch(e){
   setMessage(e.message);
 }
}
 async function getQR(){try{let q=await call(`/lectures/${selected}/qr`);setToken(q.token);setMessage('QR token generated; refresh before expiry.');}catch(e){setMessage(e.message)}}
 async function mark(){if(!token.trim()){setMessage('Please paste the current teacher QR token.');return;} try{let d=await call(`/attendance?student_id=${studentId}&lecture_id=${selected}&token=${encodeURIComponent(token)}`,{method:'POST'});setMessage(d.message+' — '+d.student);await refresh();}catch(e){setMessage(e.message)}}
 return <div className="app"><aside><div className="brand"><div className="brandicon">A</div><div><b>AttendX</b><small>SMART CAMPUS</small></div></div><div className="navlabel">WORKSPACE</div><button className={mode==='teacher'?'nav active':'nav'} onClick={()=>setMode('teacher')}><LayoutDashboard size={18}/> Teacher Dashboard</button><button className={mode==='student'?'nav active':'nav'} onClick={()=>setMode('student')}><GraduationCap size={18}/> Student Portal</button><div className="sidefoot"><ShieldCheck size={18}/> Secure attendance<br/><small>Hackathon prototype v1.0</small></div></aside><main><header><div><span className="eyebrow">CAMPUS INTELLIGENCE PLATFORM</span><h1>{mode==='teacher'?'Teacher Dashboard':'Student Portal'}</h1><p>Welcome to your smart attendance workspace.</p></div><div className="avatar">AX</div></header>
 <section className="stats"><div className="stat"><span>Total students</span><strong>{students.length||'—'}</strong><Users/></div><div className="stat"><span>Active lectures</span><strong>{lectures.filter(x=>x.active).length||0}</strong><BookOpen/></div><div className="stat"><span>Present today*</span><strong>{rows.length}</strong><CircleCheck/></div><div className="stat"><span>System status</span><strong className="green">Ready</strong><ShieldCheck/></div></section>
 {mode==='teacher'?<><section className="panel"><div className="panelhead"><div><span className="eyebrow">LECTURE CONTROL</span><h2>Start a classroom session</h2></div><span className="pill">● LIVE CONTROL</span></div><div className="formgrid"><label>Subject<input placeholder="Enter subject name" maxLength="120" value={subject} onChange={e=>setSubject(e.target.value)}/></label><label>Classroom<input placeholder="Enter classroom" maxLength="80" value={room} onChange={e=>setRoom(e.target.value)}/></label></div><div className="actions"><button className="primary" onClick={start}>＋ Start lecture</button><select value={selected} onChange={e=>setSelected(e.target.value)}><option value="">Select lecture</option>{lectures.map(l=><option value={l.id} key={l.id}>#{l.id} · {l.subject}</option>)}</select><button className="secondary" onClick={getQR} disabled={!selected}><QrCode size={17}/> Generate QR token</button></div>{token&&<div className="token"><div><b>Session QR code</b><small>Short-lived demo QR · generate a fresh code when it expires</small><img className="qrimage" src={`${api}/lectures/${selected}/qr-image?token=${encodeURIComponent(token)}`} alt="Current lecture QR code"/><code>{token}</code></div><button className="secondary" onClick={()=>navigator.clipboard?.writeText(token)}>Copy token</button></div>}</section><section className="panel"><div className="panelhead"><div><span className="eyebrow">LIVE RECORDS</span><h2>Attendance register</h2></div><div className="actions"><button className="secondary" onClick={refresh}><RefreshCw size={16}/> Refresh</button><a className="primary linkbtn" href={api+'/attendance/export'}><Download size={16}/> Export CSV</a></div></div><div className="tablewrap"><table><thead><tr><th>Student</th><th>Roll no.</th><th>Subject</th><th>Time</th><th>Status</th></tr></thead><tbody>{rows.map(r=><tr key={r.id}><td>{r.student}</td><td>{r.roll_number}</td><td>{r.subject}</td><td>{new Date(r.marked_at).toLocaleTimeString()}</td><td><span className="present">● {r.status}</span></td></tr>)}</tbody></table>{!rows.length&&<div className="empty">No attendance records yet. Start a lecture and mark demo attendance.</div>}</div></section></>:<section className="panel"><span className="eyebrow">STUDENT CHECK-IN</span><h2>Mark your attendance</h2><p>Choose your demo student ID and enter the current lecture QR token.</p><label>Student<select value={studentId} onChange={e=>setStudentId(e.target.value)}>{students.map(s=><option value={s.id} key={s.id}>{s.roll_number} — {s.name}</option>)}</select></label><label>Lecture<select value={selected} onChange={e=>setSelected(e.target.value)}>{lectures.map(l=><option value={l.id} key={l.id}>#{l.id} — {l.subject}</option>)}</select></label><label>QR token<input value={token} onChange={e=>setToken(e.target.value)} placeholder="Paste teacher's current QR token"/></label><button className="primary" onClick={mark}><ScanLine size={17}/> Verify & mark attendance</button><div className="note"><ShieldCheck/> Demo checks signed QR validity and prevents duplicate attendance. Face verification is not yet connected.</div></section>}
 {message&&<div className="message"><AlertCircle size={17}/>{message}</div>}<footer><span>AttendX · Smart Attendance System</span><span>*All-time records in this prototype</span></footer></main></div>
}
createRoot(document.getElementById('root')).render(<App/>);
