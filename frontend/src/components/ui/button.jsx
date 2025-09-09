import React from 'react'


export function Button({ children, className = '', ...props }) {
return (
<button
className={`inline-flex items-center gap-2 rounded-md px-4 py-2 text-sm font-medium shadow-sm ring-offset-2 focus:outline-none focus:ring-2 focus:ring-offset-2 ${className}`}
{...props}
>
{children}
</button>
)
}


export default Button