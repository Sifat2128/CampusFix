def get_verification_email_html(verification_url: str, email: str) -> str:
    """Generates an email-client-bulletproof, responsive HTML email for account verification."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verify your CampusFix account</title>
</head>
<body style="margin: 0; padding: 0; background-color: #080b16; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #eef1ff; -webkit-font-smoothing: antialiased;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #080b16; padding: 40px 15px;">
    <tr>
      <td align="center">
        <!-- Main Card Container -->
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 520px; background-color: #0f1426; border: 1px solid #1f2742; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);">
          
          <!-- Top Gradient Line -->
          <tr>
            <td height="5" style="background-color: #7c5cff; background-image: linear-gradient(90deg, #7c5cff, #22d3ee);"></td>
          </tr>

          <!-- Header / Brand Logo -->
          <tr>
            <td align="center" style="padding: 36px 30px 16px;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center">
                <tr>
                  <td align="center">
                    <span style="font-size: 26px; font-weight: 800; letter-spacing: -0.5px; color: #ffffff; text-decoration: none;">
                      Campus<span style="color: #22d3ee; font-weight: 800;">Fix</span>
                    </span>
                    <div style="font-size: 12px; color: #8b93b3; margin-top: 5px; font-weight: 500; letter-spacing: 0.2px;">
                      Campus Maintenance & Issue Management
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Hero Icon (Bulletproof HTML Email Table Cell) -->
          <tr>
            <td align="center" style="padding: 10px 30px 18px;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 0 auto;">
                <tr>
                  <td align="center" valign="middle" width="64" height="64" style="width: 64px; height: 64px; background-color: #171b30; border: 1.5px solid #7c5cff; border-radius: 50%; text-align: center; vertical-align: middle; font-size: 26px; line-height: 1;">
                    📬
                  </td>
                </tr>
              </table>
              <div style="display: inline-block; padding: 4px 14px; border-radius: 20px; background-color: rgba(124, 92, 255, 0.15); border: 1px solid rgba(124, 92, 255, 0.35); color: #22d3ee; font-size: 11px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;">
                Account Activation
              </div>
            </td>
          </tr>

          <!-- Content Body -->
          <tr>
            <td align="center" style="padding: 0 36px 28px; text-align: center;">
              <h1 style="margin: 0 0 12px; font-size: 22px; font-weight: 700; color: #ffffff; letter-spacing: -0.3px;">
                Verify your email address
              </h1>
              <p style="margin: 0 0 24px; font-size: 14.5px; line-height: 1.6; color: #a5adc9;">
                Welcome to <strong style="color: #ffffff;">CampusFix</strong>! You're one step away from reporting, voting on, and tracking campus repairs. Click the button below to verify your account for <strong style="color: #22d3ee;">{email}</strong>.
              </p>

              <!-- CTA Button -->
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 0 auto;">
                <tr>
                  <td align="center" style="border-radius: 12px; background-color: #7c5cff; background-image: linear-gradient(135deg, #7c5cff 0%, #22d3ee 100%);">
                    <a href="{verification_url}" target="_blank" style="display: inline-block; padding: 14px 34px; font-size: 15px; font-weight: 700; color: #ffffff; text-decoration: none; border-radius: 12px; letter-spacing: 0.2px;">
                      Verify My Account &rarr;
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Expiration Notice -->
              <p style="margin: 24px 0 0; font-size: 12.5px; color: #6d7596; line-height: 1.5;">
                ⏱ This verification link expires in <strong>24 hours</strong>.<br>
                If you did not create an account, you can safely disregard this email.
              </p>
            </td>
          </tr>

          <!-- Fallback Link Box -->
          <tr>
            <td style="padding: 0 32px 32px;">
              <div style="background-color: #0b0e1b; border: 1px solid #1a223a; border-radius: 12px; padding: 14px; text-align: left;">
                <p style="margin: 0 0 8px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; color: #6d7596; font-weight: 700;">
                  Button not working? Paste this link in your browser:
                </p>
                <div style="padding: 8px 10px; background-color: #070913; border-radius: 6px; border: 1px solid #151a2e; word-break: break-all;">
                  <a href="{verification_url}" style="font-family: Consolas, Monaco, monospace, sans-serif; font-size: 11px; line-height: 1.5; color: #38bdf8; text-decoration: none;">
                    {verification_url}
                  </a>
                </div>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #090c17; border-top: 1px solid #171d30; padding: 18px 30px; text-align: center;">
              <p style="margin: 0; font-size: 11.5px; color: #535a78;">
                &copy; CampusFix &bull; Automated Campus Issue Resolution Platform
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def get_password_reset_email_html(reset_url: str, email: str) -> str:
    """Generates an email-client-bulletproof, responsive HTML email for password resets."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Reset your CampusFix password</title>
</head>
<body style="margin: 0; padding: 0; background-color: #080b16; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #eef1ff; -webkit-font-smoothing: antialiased;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #080b16; padding: 40px 15px;">
    <tr>
      <td align="center">
        <!-- Main Card Container -->
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="max-width: 520px; background-color: #0f1426; border: 1px solid #1f2742; border-radius: 20px; overflow: hidden; box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);">
          
          <!-- Top Accent Line (Amber/Rose for security actions) -->
          <tr>
            <td height="5" style="background-color: #ff4d6d; background-image: linear-gradient(90deg, #ff4d6d, #ffb020);"></td>
          </tr>

          <!-- Header / Brand Logo -->
          <tr>
            <td align="center" style="padding: 36px 30px 16px;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center">
                <tr>
                  <td align="center">
                    <span style="font-size: 26px; font-weight: 800; letter-spacing: -0.5px; color: #ffffff; text-decoration: none;">
                      Campus<span style="color: #ffb020; font-weight: 800;">Fix</span>
                    </span>
                    <div style="font-size: 12px; color: #8b93b3; margin-top: 5px; font-weight: 500; letter-spacing: 0.2px;">
                      Account Security Center
                    </div>
                  </td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- Hero Icon -->
          <tr>
            <td align="center" style="padding: 10px 30px 18px;">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 0 auto;">
                <tr>
                  <td align="center" valign="middle" width="64" height="64" style="width: 64px; height: 64px; background-color: #211320; border: 1.5px solid #ff4d6d; border-radius: 50%; text-align: center; vertical-align: middle; font-size: 26px; line-height: 1;">
                    🔐
                  </td>
                </tr>
              </table>
              <div style="display: inline-block; padding: 4px 14px; border-radius: 20px; background-color: rgba(255, 77, 109, 0.15); border: 1px solid rgba(255, 77, 109, 0.35); color: #ffb020; font-size: 11px; font-weight: 700; letter-spacing: 0.8px; text-transform: uppercase;">
                Password Recovery
              </div>
            </td>
          </tr>

          <!-- Content Body -->
          <tr>
            <td align="center" style="padding: 0 36px 28px; text-align: center;">
              <h1 style="margin: 0 0 12px; font-size: 22px; font-weight: 700; color: #ffffff; letter-spacing: -0.3px;">
                Reset Your Password
              </h1>
              <p style="margin: 0 0 24px; font-size: 14.5px; line-height: 1.6; color: #a5adc9;">
                We received a request to reset the password for your CampusFix account (<strong style="color: #ffb020;">{email}</strong>). Click the button below to choose a new password:
              </p>

              <!-- CTA Button -->
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" align="center" style="margin: 0 auto;">
                <tr>
                  <td align="center" style="border-radius: 12px; background-color: #ff4d6d; background-image: linear-gradient(135deg, #ff4d6d 0%, #ffb020 100%);">
                    <a href="{reset_url}" target="_blank" style="display: inline-block; padding: 14px 34px; font-size: 15px; font-weight: 700; color: #ffffff; text-decoration: none; border-radius: 12px; letter-spacing: 0.2px;">
                      Reset Password &rarr;
                    </a>
                  </td>
                </tr>
              </table>

              <!-- Expiration Notice -->
              <p style="margin: 24px 0 0; font-size: 12.5px; color: #6d7596; line-height: 1.5;">
                🔒 This reset link is single-use and expires in <strong>24 hours</strong>.<br>
                If you did not request this, your account is safe; simply ignore this email.
              </p>
            </td>
          </tr>

          <!-- Fallback Link Box -->
          <tr>
            <td style="padding: 0 32px 32px;">
              <div style="background-color: #0b0e1b; border: 1px solid #1a223a; border-radius: 12px; padding: 14px; text-align: left;">
                <p style="margin: 0 0 8px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; color: #6d7596; font-weight: 700;">
                  Or copy and paste this link in your browser:
                </p>
                <div style="padding: 8px 10px; background-color: #070913; border-radius: 6px; border: 1px solid #151a2e; word-break: break-all;">
                  <a href="{reset_url}" style="font-family: Consolas, Monaco, monospace, sans-serif; font-size: 11px; line-height: 1.5; color: #ffb020; text-decoration: none;">
                    {reset_url}
                  </a>
                </div>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #090c17; border-top: 1px solid #171d30; padding: 18px 30px; text-align: center;">
              <p style="margin: 0; font-size: 11.5px; color: #535a78;">
                &copy; CampusFix &bull; Automated Campus Issue Resolution Platform
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


def get_verification_result_page(status: str, title: str, subtitle: str, detail: str, button_text: str = "Launch CampusFix Dashboard", redirect_url: str = "/ui") -> str:
    """Generates an aesthetic, animated glassmorphic verification landing page."""
    
    is_success = status == "success"
    is_warning = status == "warning"
    
    if is_success:
        badge_color = "#2fd18a"
        badge_bg = "rgba(47, 209, 138, 0.12)"
        badge_border = "rgba(47, 209, 138, 0.3)"
        icon_svg = """<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#2fd18a" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" class="draw-check"><polyline points="20 6 9 17 4 12"></polyline></svg>"""
        btn_gradient = "linear-gradient(135deg, #7c5cff 0%, #22d3ee 100%)"
        glow_color = "rgba(47, 209, 138, 0.25)"
    elif is_warning:
        badge_color = "#22d3ee"
        badge_bg = "rgba(34, 211, 238, 0.12)"
        badge_border = "rgba(34, 211, 238, 0.3)"
        icon_svg = """<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#22d3ee" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>"""
        btn_gradient = "linear-gradient(135deg, #7c5cff 0%, #22d3ee 100%)"
        glow_color = "rgba(34, 211, 238, 0.25)"
    else: # error
        badge_color = "#ff4d6d"
        badge_bg = "rgba(255, 77, 109, 0.12)"
        badge_border = "rgba(255, 77, 109, 0.3)"
        icon_svg = """<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#ff4d6d" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>"""
        btn_gradient = "linear-gradient(135deg, #ff4d6d 0%, #ffb020 100%)"
        glow_color = "rgba(255, 77, 109, 0.25)"

    trigger_confetti = "true" if is_success else "false"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} &bull; CampusFix</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;700;800&display=swap" rel="stylesheet">
  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: #080b16;
      color: #eef1ff;
      font-family: 'Plus Jakarta Sans', system-ui, -apple-system, sans-serif;
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 24px;
      overflow: hidden;
      position: relative;
    }}
    /* Glowing Ambient Background Orbs */
    .orb {{
      position: absolute;
      border-radius: 50%;
      filter: blur(100px);
      z-index: 0;
      pointer-events: none;
      opacity: 0.4;
      animation: floatOrb 14s ease-in-out infinite alternate;
    }}
    .orb-1 {{
      width: 450px;
      height: 450px;
      background: #7c5cff;
      top: -100px;
      left: -100px;
    }}
    .orb-2 {{
      width: 500px;
      height: 500px;
      background: #22d3ee;
      bottom: -120px;
      right: -120px;
      animation-delay: -7s;
    }}
    @keyframes floatOrb {{
      0% {{ transform: translate(0, 0) scale(1); }}
      100% {{ transform: translate(60px, 40px) scale(1.12); }}
    }}
    /* Glass Card */
    .card {{
      position: relative;
      z-index: 10;
      width: 100%;
      max-width: 480px;
      background: rgba(15, 20, 38, 0.7);
      backdrop-filter: blur(28px);
      -webkit-backdrop-filter: blur(28px);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 28px;
      padding: 44px 36px;
      text-align: center;
      box-shadow: 0 30px 80px rgba(0, 0, 0, 0.6), 0 0 50px {glow_color};
      animation: cardEnter 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    @keyframes cardEnter {{
      from {{ opacity: 0; transform: translateY(24px) scale(0.96); }}
      to {{ opacity: 1; transform: translateY(0) scale(1); }}
    }}
    /* Logo */
    .brand {{
      font-size: 22px;
      font-weight: 800;
      letter-spacing: -0.5px;
      margin-bottom: 28px;
      color: #fff;
    }}
    .brand span {{
      background: linear-gradient(120deg, #7c5cff, #22d3ee);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}
    /* Badge Icon */
    .icon-badge {{
      width: 88px;
      height: 88px;
      margin: 0 auto 24px;
      border-radius: 50%;
      background: {badge_bg};
      border: 1.5px solid {badge_border};
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 35px {glow_color};
      animation: pulse 2.5s infinite;
    }}
    @keyframes pulse {{
      0%, 100% {{ transform: scale(1); }}
      50% {{ transform: scale(1.05); }}
    }}
    /* Animated Checkmark */
    .draw-check {{
      stroke-dasharray: 48;
      stroke-dashoffset: 48;
      animation: draw 0.7s 0.2s cubic-bezier(0.65, 0, 0.45, 1) forwards;
    }}
    @keyframes draw {{
      to {{ stroke-dashoffset: 0; }}
    }}
    h1 {{
      font-size: 26px;
      font-weight: 800;
      letter-spacing: -0.5px;
      margin-bottom: 10px;
      color: #fff;
    }}
    .subtitle {{
      font-size: 15px;
      color: #8b93b3;
      line-height: 1.55;
      margin-bottom: 8px;
    }}
    .detail {{
      font-size: 13px;
      color: #5d6688;
      line-height: 1.5;
      margin-bottom: 32px;
    }}
    /* Action Button */
    .btn {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 10px;
      width: 100%;
      padding: 16px 24px;
      font-family: inherit;
      font-size: 15px;
      font-weight: 700;
      color: #fff;
      text-decoration: none;
      background: {btn_gradient};
      border: none;
      border-radius: 16px;
      cursor: pointer;
      box-shadow: 0 10px 30px rgba(124, 92, 255, 0.35);
      transition: transform 0.2s, box-shadow 0.2s, filter 0.2s;
    }}
    .btn:hover {{
      transform: translateY(-2px);
      box-shadow: 0 14px 40px rgba(124, 92, 255, 0.45);
      filter: brightness(1.08);
    }}
    .btn:active {{
      transform: translateY(0);
    }}
    .footer-note {{
      margin-top: 24px;
      font-size: 12px;
      color: #4b5272;
    }}
    /* Confetti Canvas */
    canvas#confetti {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      pointer-events: none;
      z-index: 99;
    }}
  </style>
</head>
<body>
  <div class="orb orb-1"></div>
  <div class="orb orb-2"></div>
  <canvas id="confetti"></canvas>

  <div class="card">
    <div class="brand">Campus<span>Fix</span></div>
    
    <div class="icon-badge">
      {icon_svg}
    </div>

    <h1>{title}</h1>
    <p class="subtitle">{subtitle}</p>
    <p class="detail">{detail}</p>

    <a href="{redirect_url}" class="btn" id="ctaBtn">
      <span>{button_text}</span>
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
    </a>

    <div class="footer-note" id="timerNote">Redirecting to CampusFix in <span id="sec">5</span>s...</div>
  </div>

  <script>
    // Countdown auto-redirect
    let s = 5;
    const secEl = document.getElementById('sec');
    const timer = setInterval(() => {{
      s--;
      if (secEl) secEl.textContent = s;
      if (s <= 0) {{
        clearInterval(timer);
        window.location.href = '{redirect_url}';
      }}
    }}, 1000);

    // Dynamic Confetti Effect on Success
    if ({trigger_confetti}) {{
      const cvs = document.getElementById('confetti');
      const ctx = cvs.getContext('2d');
      let w = cvs.width = window.innerWidth;
      let h = cvs.height = window.innerHeight;
      window.onresize = () => {{ w = cvs.width = window.innerWidth; h = cvs.height = window.innerHeight; }};

      const colors = ['#7c5cff', '#22d3ee', '#2fd18a', '#ffb020', '#ff4d6d'];
      const pieces = Array.from({{ length: 80 }}, () => ({{
        x: w / 2,
        y: h / 2 - 50,
        vx: (Math.random() - 0.5) * 16,
        vy: (Math.random() - 0.9) * 16,
        size: Math.random() * 8 + 4,
        color: colors[Math.floor(Math.random() * colors.length)],
        rotation: Math.random() * 360,
        vr: (Math.random() - 0.5) * 10,
        opacity: 1
      }}));

      let start = null;
      function animate(ts) {{
        if (!start) start = ts;
        ctx.clearRect(0, 0, w, h);
        let alive = false;
        pieces.forEach(p => {{
          p.x += p.vx;
          p.y += p.vy;
          p.vy += 0.35; // gravity
          p.rotation += p.vr;
          p.opacity -= 0.007;
          if (p.opacity > 0) {{
            alive = true;
            ctx.save();
            ctx.globalAlpha = Math.max(0, p.opacity);
            ctx.translate(p.x, p.y);
            ctx.rotate(p.rotation * Math.PI / 180);
            ctx.fillStyle = p.color;
            ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 1.4);
            ctx.restore();
          }}
        }});
        if (alive) requestAnimationFrame(animate);
      }}
      requestAnimationFrame(animate);
    }}
  </script>
</body>
</html>"""
