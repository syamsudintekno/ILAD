"""Reusable footer component for ILAD presentation pages."""

import streamlit as st


def render_footer() -> None:
    """Render the ILAD research-prototype footer."""
    st.markdown(
        """
        <div style="border-top: 1px solid #DDE7E8; color: #64748B;
                    font-size: 0.78rem; line-height: 1.5; margin-top: 2.5rem;
                    padding-top: 1rem;">
        <strong>Institutional Learning Analytics Dashboard (ILAD)</strong><br>
        Version 0.1 Research Prototype<br>
        Developed under the 2026 Interdisciplinary Research Grant<br>
        Ministry of Religious Affairs (Kementerian Agama RI)<br>
        Funding Source: DIPA 2026<br>
        © 2026
        </div>
        """,
        unsafe_allow_html=True,
    )
