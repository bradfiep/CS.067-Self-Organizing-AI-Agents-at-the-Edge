import { render } from '@testing-library/react'
import { expect, test } from 'vitest'
import App from './App'

test('App renders successfully', () => {
  render(<App />)
  // Just check that the app renders without crashing
  expect(document.body).toBeTruthy()
})
