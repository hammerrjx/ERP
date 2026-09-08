import { useRef, useState } from 'react'

function usePending() {
  const running = useRef(false)
  const [pending, setPending] = useState(false)
  const run = async (callback, event) => {
    if (running.current) return
    running.current = true
    setPending(true)
    try {
      await callback?.(event)
    } finally {
      running.current = false
      setPending(false)
    }
  }
  return [pending, run]
}

export function AsyncForm({ onSubmit, children, ...props }) {
  const [pending, run] = usePending()
  return (
    <form {...props} aria-busy={pending} onSubmit={(event) => {
      event.preventDefault()
      return run(onSubmit, event)
    }}>
      <fieldset className="pending-fields" disabled={pending}>{children}</fieldset>
      {pending && <div className="pending-status" role="status">正在处理，请稍候…</div>}
    </form>
  )
}

export function PendingButton({ onClick, disabled, children, ...props }) {
  const [pending, run] = usePending()
  return <button {...props} disabled={disabled || pending} aria-busy={pending}
    onClick={(event) => run(onClick, event)}>{children}{pending && <span role="status">处理中…</span>}</button>
}
