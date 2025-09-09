import React from 'react'


export function Input(props) {
return (
<input
{...props}
className="w-full rounded-md border px-3 py-2 text-sm placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-offset-2"
/>
)
}


export default Input