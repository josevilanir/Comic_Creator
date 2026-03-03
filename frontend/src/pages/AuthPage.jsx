import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'framer-motion';
import {
  User,
  Mail,
  Lock,
  ArrowLeft,
  PartyPopper,
  AlertTriangle,
  BookOpen,
} from 'lucide-react';

import { useAuth } from '../contexts/AuthContext';
import { GradientBackground } from '../components/ui/GradientBackground';
import { GlassButton } from '../components/ui/GlassButton';
import { BlurFade } from '../components/ui/BlurFade';
import { ConfettiCanvas } from '../components/ui/ConfettiCanvas';
import { AuthStepInput } from '../components/ui/AuthStepInput';

// ─── Step configuration ──────────────────────────────────────────────────────

const LOGIN_STEPS = ['username', 'password'];
const REGISTER_STEPS = ['username', 'email', 'password', 'confirm'];

const STEP_META = {
  username: {
    icon: <User size={18} />,
    label: 'Usuário',
    placeholder: 'Seu nome de usuário',
    type: 'text',
    showToggle: false,
    validate: (v) => v.trim().length > 0,
  },
  email: {
    icon: <Mail size={18} />,
    label: 'E-mail',
    placeholder: 'seu@email.com',
    type: 'email',
    showToggle: false,
    validate: (v) => /\S+@\S+\.\S+/.test(v),
  },
  password: {
    icon: <Lock size={18} />,
    label: 'Senha',
    placeholder: 'Mínimo 6 caracteres',
    type: 'password',
    showToggle: true,
    validate: (v) => v.length >= 6,
  },
  confirm: {
    icon: <Lock size={18} />,
    label: 'Confirmar senha',
    placeholder: 'Repita a senha',
    type: 'password',
    showToggle: true,
    validate: (v) => v.length >= 6,
  },
};

// ─── Titles per mode & step ───────────────────────────────────────────────────

function getTitle(mode, step) {
  if (step === 0) {
    return mode === 'login' ? 'Bem-vindo\nde volta' : 'Crie sua\nconta';
  }
  const titles = {
    login: { 1: 'Sua senha' },
    register: { 1: 'Seu e-mail', 2: 'Sua senha', 3: 'Confirme a senha' },
  };
  return titles[mode][step] ?? '';
}

function getSubtitle(mode, step) {
  if (step === 0) {
    return mode === 'login'
      ? 'Digite seu usuário para continuar'
      : 'Como devemos te chamar?';
  }
  const subs = {
    login: { 1: 'Digite sua senha para entrar' },
    register: {
      1: 'Para recuperar sua conta depois',
      2: 'Use ao menos 6 caracteres',
      3: 'Só para garantir que está certo',
    },
  };
  return subs[mode][step] ?? '';
}

// ─── Motion variants ──────────────────────────────────────────────────────────

const titleVariants = {
  initial: { opacity: 0, y: 12, filter: 'blur(4px)' },
  animate: { opacity: 1, y: 0, filter: 'blur(0px)', transition: { duration: 0.35, ease: [0.21, 0.47, 0.32, 0.98] } },
  exit:    { opacity: 0, y: -12, filter: 'blur(4px)', transition: { duration: 0.22 } },
};

const modalVariants = {
  initial: { opacity: 0, scale: 0.92, y: 20 },
  animate: { opacity: 1, scale: 1, y: 0,  transition: { duration: 0.3, ease: [0.21, 0.47, 0.32, 0.98] } },
  exit:    { opacity: 0, scale: 0.9, y: 10, transition: { duration: 0.2 } },
};

const overlayVariants = {
  initial: { opacity: 0 },
  animate: { opacity: 1, transition: { duration: 0.25 } },
  exit:    { opacity: 0, transition: { duration: 0.2 } },
};

// ─── TextLoop component ───────────────────────────────────────────────────────

function TextLoop({ texts, interval = 1800 }) {
  const [idx, setIdx] = useState(0);
  useEffect(() => {
    const id = setInterval(() => setIdx((i) => (i + 1) % texts.length), interval);
    return () => clearInterval(id);
  }, [texts, interval]);
  return (
    <AnimatePresence mode="wait">
      <motion.span
        key={idx}
        initial={{ opacity: 0, y: 6 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -6 }}
        transition={{ duration: 0.3 }}
        style={{ display: 'block' }}
      >
        {texts[idx]}
      </motion.span>
    </AnimatePresence>
  );
}

// ─── Status Modal ─────────────────────────────────────────────────────────────

function StatusModal({ status, errorMessage, onRetry }) {
  return (
    <AnimatePresence>
      {status !== 'closed' && (
        <motion.div
          className="auth-modal-overlay"
          variants={overlayVariants}
          initial="initial"
          animate="animate"
          exit="exit"
        >
          <motion.div
            className="auth-modal"
            variants={modalVariants}
            initial="initial"
            animate="animate"
            exit="exit"
          >
            {status === 'loading' && (
              <>
                <div className="auth-spinner" />
                <p className="auth-modal__title">
                  <TextLoop
                    texts={['Criando sua conta...', 'Quase lá...', 'Preparando tudo...', 'Um momento...']}
                  />
                </p>
              </>
            )}

            {status === 'error' && (
              <>
                <span className="auth-modal__icon" style={{ color: '#ff5f5f' }}>
                  <AlertTriangle size={40} />
                </span>
                <p className="auth-modal__title">Algo deu errado</p>
                {errorMessage && (
                  <p className="auth-modal__message">{errorMessage}</p>
                )}
                <GlassButton size="sm" onClick={onRetry}>
                  Tentar novamente
                </GlassButton>
              </>
            )}

            {status === 'success' && (
              <>
                <span className="auth-modal__icon">
                  <PartyPopper size={40} style={{ color: 'var(--coral)' }} />
                </span>
                <p className="auth-modal__title">Seja bem-vindo!</p>
                <p className="auth-modal__message">Redirecionando para sua biblioteca...</p>
              </>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

// ─── Main AuthPage ────────────────────────────────────────────────────────────

export function AuthPage() {
  const navigate = useNavigate();
  const { login, register } = useAuth();

  const [mode, setMode] = useState('login');
  const [step, setStep] = useState(0);
  const [fields, setFields] = useState({ username: '', email: '', password: '', confirm: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [modalStatus, setModalStatus] = useState('closed'); // 'closed'|'loading'|'error'|'success'

  const confettiRef = useRef(null);
  const inputRefs = useRef({});

  const steps = mode === 'login' ? LOGIN_STEPS : REGISTER_STEPS;
  const currentField = steps[step];
  const meta = STEP_META[currentField];
  const isValid = meta.validate(fields[currentField]);

  // Auto-focus the current field when step changes
  useEffect(() => {
    const timer = setTimeout(() => {
      inputRefs.current[currentField]?.focus();
    }, 120);
    return () => clearTimeout(timer);
  }, [step, mode, currentField]);

  function handleFieldChange(fieldName, value) {
    setFields((prev) => ({ ...prev, [fieldName]: value }));
  }

  function handleAdvance() {
    if (!isValid) return;
    if (step < steps.length - 1) {
      setStep(step + 1);
    } else {
      handleSubmit();
    }
  }

  function handleBack() {
    if (step === 0) return;
    const prev = steps[step];
    setFields((f) => ({ ...f, [prev]: '' }));
    setStep(step - 1);
  }

  async function handleSubmit() {
    setError('');
    setLoading(true);

    if (mode === 'register' && fields.password !== fields.confirm) {
      setError('As senhas não coincidem. Tente novamente.');
      setModalStatus('error');
      setLoading(false);
      return;
    }

    if (mode === 'login') {
      try {
        await login(fields.username, fields.password);
        navigate('/library');
      } catch (err) {
        const msg =
          err.response?.data?.data?.message ||
          err.response?.data?.data?.fields?.join(', ') ||
          err.response?.data?.message ||
          'Credenciais inválidas. Tente novamente.';
        setError(msg);
        setModalStatus('error');
      } finally {
        setLoading(false);
      }
    } else {
      setModalStatus('loading');
      try {
        await register(fields.username, fields.email, fields.password);
        confettiRef.current?.fire({ particleCount: 80 });
        setModalStatus('success');
        setTimeout(() => navigate('/library'), 1500);
      } catch (err) {
        const msg =
          err.response?.data?.data?.message ||
          err.response?.data?.data?.fields?.join(', ') ||
          err.response?.data?.message ||
          'Erro ao criar conta. Tente novamente.';
        setError(msg);
        setModalStatus('error');
      } finally {
        setLoading(false);
      }
    }
  }

  function switchMode(newMode) {
    setMode(newMode);
    setStep(0);
    setFields({ username: '', email: '', password: '', confirm: '' });
    setError('');
    setModalStatus('closed');
  }

  function handleRetry() {
    setModalStatus('closed');
    setError('');
    setLoading(false);
  }

  const title = getTitle(mode, step);
  const subtitle = getSubtitle(mode, step);

  return (
    <>
      <GradientBackground />
      <ConfettiCanvas ref={confettiRef} manualstart />

      {/* Logo — top left */}
      <div className="auth-logo">
        <div className="auth-logo__icon">
          <BookOpen size={18} />
        </div>
        <span className="auth-logo__name">Comic Creator</span>
      </div>

      {/* Status modal */}
      <StatusModal status={modalStatus} errorMessage={error} onRetry={handleRetry} />

      {/* Main card */}
      <div className="auth-screen">
        <div className="auth-card">
          <fieldset
            disabled={modalStatus !== 'closed'}
            style={{ border: 'none', padding: 0, margin: 0 }}
          >
            {/* Step dots */}
            {steps.length > 1 && (
              <BlurFade delay={0.05}>
                <div className="auth-dots">
                  {steps.map((_, i) => (
                    <span
                      key={i}
                      className={`auth-dot${i === step ? ' auth-dot--active' : i < step ? ' auth-dot--done' : ''}`}
                    />
                  ))}
                </div>
              </BlurFade>
            )}

            {/* Title block */}
            <AnimatePresence mode="wait">
              <motion.div
                key={`${mode}-${step}`}
                variants={titleVariants}
                initial="initial"
                animate="animate"
                exit="exit"
                style={{ marginBottom: 0 }}
              >
                <h1 className="auth-title" style={{ whiteSpace: 'pre-line' }}>
                  {title}
                </h1>
                <p className="auth-subtitle">{subtitle}</p>
              </motion.div>
            </AnimatePresence>

            {/* Form */}
            <form onSubmit={(e) => e.preventDefault()} className="auth-step-form">
              <AnimatePresence mode="wait">
                <motion.div
                  key={`${mode}-input-${step}`}
                  initial={{ opacity: 0, x: 20, filter: 'blur(4px)' }}
                  animate={{ opacity: 1, x: 0, filter: 'blur(0px)', transition: { duration: 0.3, ease: [0.21, 0.47, 0.32, 0.98] } }}
                  exit={{ opacity: 0, x: -20, filter: 'blur(4px)', transition: { duration: 0.2 } }}
                >
                  <AuthStepInput
                    icon={meta.icon}
                    label={meta.label}
                    placeholder={meta.placeholder}
                    type={meta.type}
                    showToggle={meta.showToggle}
                    value={fields[currentField]}
                    onChange={(v) => handleFieldChange(currentField, v)}
                    isValid={isValid}
                    onAdvance={handleAdvance}
                    inputRef={(el) => (inputRefs.current[currentField] = el)}
                  />
                </motion.div>
              </AnimatePresence>

              {/* Submit / advance button */}
              <BlurFade delay={0.1}>
                <GlassButton
                  type="button"
                  onClick={handleAdvance}
                  disabled={!isValid || loading}
                >
                  {loading && mode === 'login'
                    ? 'Entrando...'
                    : step < steps.length - 1
                    ? 'Continuar'
                    : mode === 'login'
                    ? 'Entrar'
                    : 'Criar conta'}
                </GlassButton>
              </BlurFade>

              {/* Back button */}
              <AnimatePresence>
                {step > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 6 }}
                    transition={{ duration: 0.2 }}
                    style={{ display: 'flex', justifyContent: 'center' }}
                  >
                    <button type="button" className="auth-back-btn" onClick={handleBack}>
                      <ArrowLeft size={15} />
                      Voltar
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>
            </form>

            {/* Toggle login / register */}
            <p className="auth-switch">
              {mode === 'login' ? (
                <>
                  Não tem conta?{' '}
                  <button type="button" onClick={() => switchMode('register')}>
                    Criar conta
                  </button>
                </>
              ) : (
                <>
                  Já tem conta?{' '}
                  <button type="button" onClick={() => switchMode('login')}>
                    Entrar
                  </button>
                </>
              )}
            </p>
          </fieldset>
        </div>
      </div>
    </>
  );
}
