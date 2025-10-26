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
    // make the header span the full viewport width so left/right alignments work
    <header
      style={{
        display: 'flex',
        position: 'fixed',
        top: 0,
        left: 0,
        padding: '10px 20px',
        alignItems: 'left',
        justifyContent: 'space-between',
        width: '100vw',
        borderBottom: '2px solid #000000ff',
        boxSizing: 'border-box'
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
        {logoSrc && (
          <img src={logoSrc} alt={logoAlt} style={{ height: 36, objectFit: 'contain' }} />
        )}
        {link ? (
          <a href={link} style={{ textDecoration: 'none', color: 'inherit' }}>
            <h2 className="OSUHeader">{title}</h2>
          </a>
        ) : (
          <h2 className="OSUHeader">{title}</h2>
        )}
      </div>

      <nav style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
        {actions}
      </nav>
    </header>
  )
}
