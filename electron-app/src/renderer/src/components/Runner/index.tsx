import { Box, Modal, Typography, CircularProgress, Button } from '@mui/material'
import { useEffect, useRef, useState } from 'react'

const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  pt: 2,
  px: 4,
  pb: 3,
  width: '75%',
  maxHeight: '80%',
  overflow: 'auto'
}

export const Runner = ({ handleClose }: { handleClose: any }) => {
  const [output, setOutput] = useState<string>('')
  const [isRunning] = useState<boolean>(true)
  const outputRef = useRef<HTMLPreElement>(null)

  useEffect(() => {
    window.electron.onCmdOutput((data: any) => {
      setOutput((prev) => (prev ? `${prev}\n${data}` : data))
    })
  }, [])

  const handleTerminate = () => {
    window.electron.terminateCmd()
    handleClose(false)
  }

  useEffect(() => {
    if (outputRef.current) {
      outputRef.current.scrollTop = outputRef.current.scrollHeight
    }
  }, [output])

  return (
    <Modal
      open={true}
      onClose={handleClose}
      aria-labelledby="terminal-modal-title"
      aria-describedby="terminal-modal-description"
    >
      <Box sx={style}>
        <Typography id="terminal-modal-title" variant="h6" component="h2">
          Running SpeCollate
        </Typography>
        <Typography id="terminal-modal-description" sx={{ mb: 2 }}>
          Output from command:
        </Typography>
        {isRunning && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <CircularProgress size={20} />
            <Typography variant="body2">Processing...</Typography>
          </Box>
        )}
        <pre
          ref={outputRef}
          style={{
            fontFamily: 'Consolas, Monaco, "Andale Mono", "Ubuntu Mono", monospace',
            background: '#f4f4f4',
            padding: '8px',
            borderRadius: '4px',
            maxHeight: '400px',
            overflow: 'auto'
          }}
        >
          {output || 'Waiting for output...'}
        </pre>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', mt: 2 }}>
          <Button variant="contained" color="error" onClick={handleTerminate} disabled={!isRunning}>
            Terminate
          </Button>
        </Box>
      </Box>
    </Modal>
  )
}
