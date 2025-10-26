import React from 'react'

type HeaderProps = {
  title: string
  logoSrc?: string
  logoAlt?: string
  actions?: React.ReactNode
  link?: string
}

export default function Header({ title, logoSrc, logoAlt = 'logo', actions, link }: HeaderProps) {
  return (
    <header style={{ display: 'flex', alignItems: 'center', gap: '1rem', justifyContent: 'space-between', width: '100%' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
        {logoSrc && (
          <img src={logoSrc} alt={logoAlt} style={{ height: 36 }} />
        )}
        {link ? (
          <a href={link} style={{ textDecoration: 'none', color: 'inherit' }}>
            <h2 className="OSUHeader">{title}</h2>
          </a>
        ) : (
          <h2 className="OSUHeader">{title}</h2>
        )}
      </div>

      <div>
        {actions}
      </div>
    </header>
  )
}
