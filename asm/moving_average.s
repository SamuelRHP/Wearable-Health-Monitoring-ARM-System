/*
 * Wearable Health-Monitoring ARM System
 * 4-Sample Moving Average Filter and Threshold Comparator
 *
 * Target Architecture: ARM Cortex-M (Thumb-1 / Thumb-2 ISA)
 * Student: Samuel Rohlupuia
 *
 * Calling Convention (ARM AAPCS):
 *   Input:
 *     r0: Pointer to 4 contiguous 16-bit signed Q15 samples (halfwords) in SRAM
 *     r1: 16-bit signed Q15 threshold value
 *   Output:
 *     r0: Alert flag (1 = threshold exceeded, 0 = normal)
 *     r2: Filtered 16-bit signed Q15 average: sum(sample[0..3]) >> 2
 *   Clobbered:
 *     r2, r3, APSR flags
 */

    .syntax unified
    .thumb
    .text
    .align 2
    .global moving_average_4

moving_average_4:
    /* Step 1: Load sample 0 and sign-extend to 32 bits */
    ldrh    r2, [r0, #0]        /* r2 = sample[0] (unsigned 16-bit load)       */
    sxth    r2, r2              /* r2 = sign_extend_16(r2) (initializes sum)   */

    /* Step 2: Load sample 1 and accumulate */
    ldrh    r3, [r0, #2]        /* r3 = sample[1]                              */
    sxth    r3, r3              /* r3 = sign_extend_16(r3)                     */
    adds    r2, r2, r3          /* r2 = sum = sample[0] + sample[1]            */

    /* Step 3: Load sample 2 and accumulate */
    ldrh    r3, [r0, #4]        /* r3 = sample[2]                              */
    sxth    r3, r3              /* r3 = sign_extend_16(r3)                     */
    adds    r2, r2, r3          /* r2 = sum += sample[2]                       */

    /* Step 4: Load sample 3 and accumulate */
    ldrh    r3, [r0, #6]        /* r3 = sample[3]                              */
    sxth    r3, r3              /* r3 = sign_extend_16(r3)                     */
    adds    r2, r2, r3          /* r2 = sum += sample[3]                       */

    /* Step 5: Compute 4-sample arithmetic mean using ASR #2 */
    asrs    r2, r2, #2          /* r2 = sum >> 2 (arithmetic shift preserves sign) */

    /* Step 6: Compare computed average with physiological threshold */
    cmp     r2, r1              /* APSR flags set based on (average - threshold) */
    bgt     alert_high          /* If average > threshold, branch to alert     */

normal:
    movs    r0, #0              /* r0 = 0 (no alert)                           */
    b       done                /* Skip alert block                            */

alert_high:
    movs    r0, #1              /* r0 = 1 (alert active)                       */

done:
    nop                         /* Pipeline termination / return marker        */
