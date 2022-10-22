import styles from './style.module.css'
import { Container, LinkComponent } from '../index'

const Footer = ({ onThemeSwitch }) => {
  return <footer className={styles.footer}>
    <Container className={styles.footer__container}>
      <LinkComponent href='#' title='Продуктовый помощник' className={styles.footer__brand} />
      <div onClick={onThemeSwitch} className={styles.footer__theme_icon}></div>
    </Container>
  </footer>
}

export default Footer
