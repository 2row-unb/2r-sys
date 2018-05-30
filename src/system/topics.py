"""
Module to define Gabby topics
"""
import gabby

topics = {
   "kernel_receiver":           gabby.Topic('2rs/receiver/input', 'i'*23),
   "receiver_controller":       gabby.Topic('2rs/receiver/output', 'i'*23),
   "controller_transmitter":    gabby.Topic('2rs/trasmitter/input', 'i'*23),
   "trasmitter_kernel":         gabby.Topic('2rs/transmitter/output', 'i'*23),
   "controller_processor":      gabby.Topic('2rs/processor/input', 'i'*23),
   "processor_controller":      gabby.Topic('2rs/processor/output', 'i'*23),
}
