interface ResponsiveTableProps {
  children: React.ReactNode
  className?: string
}

export default function ResponsiveTable({ children, className = '' }: ResponsiveTableProps) {
  return (
    <div className={`overflow-x-auto -mx-4 sm:-mx-6 md:mx-0 ${className}`}>
      <div className="inline-block min-w-full px-4 sm:px-6 md:px-0 align-middle">
        {children}
      </div>
    </div>
  )
}
