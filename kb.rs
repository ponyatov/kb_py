//! kb: Knowledge Base engine in Rust
//! (c) Dmitry Ponyatov <<dponyatov@gmail.com>> 2020 MIT
//! github: https://github.com/ponyatov/kb

use std::env;

// pub enum Object {
//     Object(String),
//     Symbol(String),
//     Number(f32),
//     Integer(i32),
//     Operator(String),
// }

#[allow(dead_code)]
/// print arguments
fn args() {
    // arguments counter
    let argc: usize = env::args().count();
    assert!(argc > 1);
    // arguments vector
    let argv: Vec<String> = env::args().collect();
    // loop with count
    let mut count = 0;
    for arg in argv {
        println!("argv[{:?}] = {:?}", count, arg);
        count += 1;
    }
}

// Rust workout
// https://stevedonovan.github.io/rust-gentle-intro/readme.html#a-gentle-introduction-to-rust
// https://stevedonovan.github.io/rust-gentle-intro/1-basics.html

fn quad(x: f32) -> f32 {
    x * x
}

fn main() {
    let mut s = 0.0;
    for i in 0..5 {
        println!(
            "{:?} {:?} {:?}",
            i,
            if i % 2 == 0 { "even" } else { "odd" },
            s
        );
        s += quad(s + i as f32);
    }
}
