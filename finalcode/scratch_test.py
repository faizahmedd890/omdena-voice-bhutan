import streamlit as st
import time
import uuid

# Inject the global JS player once
st.components.v1.html("""
<script>
    const parentWin = window.parent;
    if (!parentWin.audioQueue) {
        parentWin.audioQueue = [];
        parentWin.isPlaying = false;
        parentWin.isMuted = false;

        parentWin.playNext = function() {
            if (parentWin.audioQueue.length > 0) {
                parentWin.isPlaying = true;
                let src = parentWin.audioQueue.shift();
                let audio = new Audio(src);
                audio.muted = parentWin.isMuted;
                parentWin.currentAudio = audio;

                audio.onended = function() {
                    parentWin.currentAudio = null;
                    parentWin.playNext();
                };
                audio.play().catch(e => {
                    console.error("Audio playback failed", e);
                    parentWin.playNext();
                });
            } else {
                parentWin.isPlaying = false;
            }
        };

        parentWin.enqueueAudio = function(src) {
            parentWin.audioQueue.push(src);
            if (!parentWin.isPlaying) {
                parentWin.playNext();
            }
        };

        parentWin.toggleMute = function() {
            parentWin.isMuted = !parentWin.isMuted;
            if (parentWin.currentAudio) {
                parentWin.currentAudio.muted = parentWin.isMuted;
            }
            return parentWin.isMuted;
        };
    }
</script>
""", height=0, width=0)

if st.button("Test Enqueue with Keys"):
    ph = st.empty()
    for i in range(3):
        # Unique key ensures Streamlit mounts a new iframe each time
        st.components.v1.html(
            f"<script>window.parent.enqueueAudio('test_{i}');</script>",
            height=0, width=0, key=uuid.uuid4().hex
        )
        time.sleep(1)
